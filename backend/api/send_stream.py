import os
import json
from typing import List, Dict
import random
import time
from datetime import datetime
import asyncio
import threading

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks

from utils.kafka_producer import KafkaProducerWrapper, send_data_to_kafka
from utils.file_management import (
    create_folder,
    save_json_file,
    device_exists,
    validate_data
)

from backend.config.config import HISTORICAL_DATA_PATH, SCHEMA_DATA_PATH
router = APIRouter()

# Constants
SCHEMA_SAVE_PATH: str = SCHEMA_DATA_PATH
ENDPOINT_WEBSOCKET: str = "/send-stream/{device_id}/{run_id}"
ENDPOINT_START_STREAM: str = "/generate-synthetic-data/{num_players}/{run_id}/{duration}"
ENDPOINT_STOP_STREAM: str = "/stop-stream/{run_id}"

# Constants
PITCH_LAT_MIN, PITCH_LAT_MAX = 40.0, 40.0009
PITCH_LON_MIN, PITCH_LON_MAX = -75.0012, -75.0
STEP_SIZE_LAT, STEP_SIZE_LON = 0.00001, 0.000015
HR_MIN, HR_MAX = 70, 140
TEMP_MIN, TEMP_MAX = 36.0, 39.0
HR_OUT_OF_BOUNDS_LOW, HR_OUT_OF_BOUNDS_HIGH = (30, 60), (160, 200)
TEMP_OUT_OF_BOUNDS_LOW, TEMP_OUT_OF_BOUNDS_HIGH = (34.0, 35.5), (39.5, 42.0)
INTERVAL_SECONDS = 0.5

# State to manage background streaming tasks
streaming_tasks = {}
lock = threading.Lock()


def random_walk(current_lat, current_lon):
    """Perform a random walk within the boundaries of the football pitch."""
    new_lat = current_lat + random.uniform(-STEP_SIZE_LAT, STEP_SIZE_LAT)
    new_lon = current_lon + random.uniform(-STEP_SIZE_LON, STEP_SIZE_LON)
    new_lat = max(min(new_lat, PITCH_LAT_MAX), PITCH_LAT_MIN)
    new_lon = max(min(new_lon, PITCH_LON_MAX), PITCH_LON_MIN)
    return new_lat, new_lon


def gradual_change(value, min_value, max_value, step, increasing):
    """Adjust a value gradually up or down."""
    if increasing:
        value += step
        if value >= max_value:
            value = max_value
            increasing = False
    else:
        value -= step
        if value <= min_value:
            value = min_value
            increasing = True
    return value, increasing


async def stream_synthetic_data(run_id, num_players, duration):
    """Stream synthetic data."""
    end_time = asyncio.get_event_loop().time() + duration
    next_out_of_bounds_time = random.uniform(30, 100)
    last_out_of_bounds_time = 0
    players_data = {
        f"player_{i}": {
            "lat": (PITCH_LAT_MIN + PITCH_LAT_MAX) / 2,
            "lon": (PITCH_LON_MIN + PITCH_LON_MAX) / 2,
            "hr": HR_MIN,
            "temp": TEMP_MIN,
            "hr_increasing": True,
            "temp_increasing": True
        } for i in range(num_players)
    }

    while asyncio.get_event_loop().time() < end_time:
        if run_id not in streaming_tasks:
            print(f"Streaming for run {run_id} stopped.")
            break

        current_time = asyncio.get_event_loop().time()
        out_of_bounds_mode = False

        if current_time - last_out_of_bounds_time > next_out_of_bounds_time:
            out_of_bounds_mode = True
            last_out_of_bounds_time = current_time
            next_out_of_bounds_time = random.uniform(30, 100)

        for player_id, data in players_data.items():
            lat, lon = random_walk(data["lat"], data["lon"])
            hr, hr_increasing = gradual_change(data["hr"], HR_MIN, HR_MAX, 2, data["hr_increasing"])
            temp, temp_increasing = gradual_change(data["temp"], TEMP_MIN, TEMP_MAX, 0.1, data["temp_increasing"])

            if out_of_bounds_mode:
                hr = random.randint(*HR_OUT_OF_BOUNDS_LOW) if random.random() < 0.5 else random.randint(*HR_OUT_OF_BOUNDS_HIGH)
                temp = random.uniform(*TEMP_OUT_OF_BOUNDS_LOW) if random.random() < 0.5 else random.uniform(*TEMP_OUT_OF_BOUNDS_HIGH)

            players_data[player_id] = {
                "lat": lat,
                "lon": lon,
                "hr": hr,
                "temp": temp,
                "hr_increasing": hr_increasing,
                "temp_increasing": temp_increasing
            }

            data_message = {
                "device_id": player_id,
                "run_id": run_id,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "heart_rate": hr,
                "temperature": temp,
                "timestamp": datetime.utcnow().isoformat()
            }

            print(f"Streaming data: {json.dumps(data_message)}")  # Replace with sending to Kafka, etc.

        await asyncio.sleep(INTERVAL_SECONDS)


@router.websocket(ENDPOINT_WEBSOCKET)
async def send_stream(
    websocket: WebSocket,
    device_id: str,
    run_id: str
) -> None:
    """
    WebSocket endpoint to send a stream of data for a device and run.

    This endpoint listens for data from the WebSocket, validates it, and sends it to Kafka.
    It also handles disconnections and stores historical data upon WebSocket closure.

    Args:
        websocket (WebSocket): The WebSocket connection.
        device_id (str): The ID of the device.
        run_id (str): The ID of the run associated with the device.

    Returns:
        None
    """
    await websocket.accept()
    data_list: List[Dict] = []
    producer: KafkaProducerWrapper = None

    try:
        device_schema = device_exists(SCHEMA_SAVE_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]
        producer = KafkaProducerWrapper()

        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)

            valid = await process_received_data(websocket, device_id, run_id, data, schema_fields, producer, data_list)

            if not valid:
                await websocket.send_text("Closing connection due to validation error.")
                await websocket.close(code=1003)
                break

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for device '{device_id}'.")
    except Exception as e:
        print(f"Error in send_stream: {e}")
        await websocket.close(code=1006)
    finally:
        if producer:
            producer.flush()
            producer.close()
        await handle_websocket_disconnect(device_id, run_id, data_list)


async def handle_websocket_disconnect(
    device_id: str,
    run_id: str,
    data_list: List[Dict]
) -> None:
    """
    Handles WebSocket disconnection, including saving historical data.
    """
    device_run_path: str = os.path.join(HISTORICAL_DATA_PATH, device_id, run_id)
    create_folder(device_run_path)
    historical_file: str = os.path.join(device_run_path, f"{device_id}.json")

    try:
        if os.path.exists(historical_file):
            with open(historical_file, "r") as file:
                existing_data = json.load(file)
            existing_data.extend(data_list)
            save_json_file(historical_file, existing_data)
        else:
            save_json_file(historical_file, data_list)
        print(f"Historical data saved for device '{device_id}'.")
    except Exception as e:
        print(f"Failed to save historical data: {e}")


async def process_received_data(
    websocket: WebSocket,
    device_id: str,
    run_id: str,
    data: Dict,
    schema_fields: Dict,
    producer: KafkaProducerWrapper,
    data_list: List[Dict]
) -> bool:
    """
    Processes the data received from the WebSocket, validates it, and sends it to Kafka if valid.
    """
    if not validate_data(data, schema_fields):
        await websocket.send_text("Validation failed. Data does not match the schema.")
        print(f"Validation failed for device {device_id}, run {run_id}. Data: {data}")
        return False

    kafka_topic: str = f"{device_id}_{run_id}"
    send_data_to_kafka(producer, kafka_topic, data)
    data_list.append(data)

    return True


@router.post("/start-stream/{run_id}/{num_players}/{duration}")
async def start_stream(run_id: str, num_players: int, duration: int, background_tasks: BackgroundTasks):
    """
    Start streaming synthetic data for a run.

    Args:
        run_id (str): ID of the run.
        num_players (int): Number of players to simulate.
        duration (int): Duration of the stream in seconds.
        background_tasks (BackgroundTasks): Background task manager.

    Returns:
        JSON message confirming the stream has started.
    """
    with lock:
        if run_id in streaming_tasks:
            raise HTTPException(status_code=400, detail=f"Run {run_id} is already streaming.")

        streaming_tasks[run_id] = True
        background_tasks.add_task(stream_synthetic_data, run_id, num_players, duration)

    return {"message": f"Streaming started for run {run_id} with {num_players} players for {duration} seconds."}


@router.post("/stop-stream/{run_id}")
async def stop_stream(run_id: str):
    """
    Stop streaming synthetic data for a run.

    Args:
        run_id (str): ID of the run.

    Returns:
        JSON message confirming the stream has stopped.
    """
    with lock:
        if run_id not in streaming_tasks:
            raise HTTPException(status_code=400, detail=f"No active stream found for run {run_id}.")

        del streaming_tasks[run_id]

    return {"message": f"Streaming stopped for run {run_id}."}