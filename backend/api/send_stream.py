import os
import json
from typing import List, Dict, Any
import asyncio
import websockets
import random
import time
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

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
ENDPOINT_START_SYNTHETIC_DATA: str = "/start-synthetic-data"

# Constants
WEBSOCKET_ENDPOINT_TEMPLATE = "ws://localhost:8000/send-stream/{device_id}/{run_id}"
INTERVAL_SECONDS = 0.5
OUT_OF_BOUNDS_INTERVAL = 100

# GPS-related boundaries and step sizes
PITCH_LAT_MIN = 40.0
PITCH_LAT_MAX = 40.0009
PITCH_LON_MIN = -75.0012
PITCH_LON_MAX = -75.0
STEP_SIZE_LAT = 0.00001
STEP_SIZE_LON = 0.000015

# Heart rate boundaries
HR_MIN = 70
HR_MAX = 140
HR_OUT_OF_BOUNDS_LOW = (30, 60)
HR_OUT_OF_BOUNDS_HIGH = (160, 200)

# Temperature boundaries
TEMP_MIN = 36.0
TEMP_MAX = 39.0
TEMP_OUT_OF_BOUNDS_LOW = (34.0, 35.5)
TEMP_OUT_OF_BOUNDS_HIGH = (39.5, 42.0)


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


def random_walk(current_lat, current_lon):
    new_lat = current_lat + random.uniform(-STEP_SIZE_LAT, STEP_SIZE_LAT)
    new_lon = current_lon + random.uniform(-STEP_SIZE_LON, STEP_SIZE_LON)
    new_lat = max(min(new_lat, PITCH_LAT_MAX), PITCH_LAT_MIN)
    new_lon = max(min(new_lon, PITCH_LON_MAX), PITCH_LON_MIN)
    return new_lat, new_lon

def generate_heart_rate():
    return random.randint(HR_MIN, HR_MAX)

def generate_temperature():
    return round(random.uniform(TEMP_MIN, TEMP_MAX), 1)

async def send_synthetic_data(device_id, run_id, schema_type, duration_seconds):
    websocket_endpoint = WEBSOCKET_ENDPOINT_TEMPLATE.format(device_id=device_id, run_id=run_id)

    async with websockets.connect(websocket_endpoint) as websocket:
        start_time = time.time()
        end_time = start_time + duration_seconds
        current_lat = (PITCH_LAT_MIN + PITCH_LAT_MAX) / 2
        current_lon = (PITCH_LON_MIN + PITCH_LON_MAX) / 2
        message_count = 0

        while time.time() < end_time:
            if schema_type == "gps":
                if message_count % OUT_OF_BOUNDS_INTERVAL == 0 and message_count > 0:
                    out_of_bounds_lat = PITCH_LAT_MAX + random.uniform(0.0001, 0.0005)
                    out_of_bounds_lon = PITCH_LON_MAX + random.uniform(0.0001, 0.0005)
                    data = {
                        "latitude": round(out_of_bounds_lat, 6),
                        "longitude": round(out_of_bounds_lon, 6),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    current_lat, current_lon = random_walk(current_lat, current_lon)
                    data = {
                        "latitude": round(current_lat, 6),
                        "longitude": round(current_lon, 6),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            elif schema_type == "heart_rate":
                if message_count % OUT_OF_BOUNDS_INTERVAL == 0 and message_count > 0:
                    out_of_bounds_hr = random.choice(
                        [random.randint(*HR_OUT_OF_BOUNDS_LOW), random.randint(*HR_OUT_OF_BOUNDS_HIGH)]
                    )
                    data = {
                        "heart_rate": out_of_bounds_hr,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    heart_rate = generate_heart_rate()
                    data = {
                        "heart_rate": heart_rate,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            elif schema_type == "temperature":
                if message_count % OUT_OF_BOUNDS_INTERVAL == 0 and message_count > 0:
                    out_of_bounds_temp = random.choice(
                        [round(random.uniform(*TEMP_OUT_OF_BOUNDS_LOW), 1), round(random.uniform(*TEMP_OUT_OF_BOUNDS_HIGH), 1)]
                    )
                    data = {
                        "temperature": out_of_bounds_temp,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    temperature = generate_temperature()
                    data = {
                        "temperature": temperature,
                        "timestamp": datetime.utcnow().isoformat()
                    }

            data_str = json.dumps(data)
            await websocket.send(data_str)
            print(f"Sent data from {device_id} (run {run_id}): {data_str}")

            message_count += 1
            await asyncio.sleep(INTERVAL_SECONDS)

@router.post(ENDPOINT_START_SYNTHETIC_DATA)
async def start_synthetic_data(num_players: int, stream_seconds: int) -> Dict:
    run_id = "run_001"

    async def main():
        tasks = [
            *[send_synthetic_data(f"gps_{i}", run_id, "gps", stream_seconds) for i in range(1, num_players + 1)],
            *[send_synthetic_data(f"player_heart_rate_{i}", run_id, "heart_rate", stream_seconds) for i in range(1, num_players + 1)],
            *[send_synthetic_data(f"player_temperature_{i}", run_id, "temperature", stream_seconds) for i in range(1, num_players + 1)]
        ]
        await asyncio.gather(*tasks)

    asyncio.create_task(main())
    return {"message": "Synthetic data stream started."}
