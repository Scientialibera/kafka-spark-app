import os
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from utils.kafka_producer import start_kafka_stream, stop_kafka_stream, send_to_kafka
from backend.api.register_device import get_device_schema
from utils.file_management import create_folder, save_json_file
from datetime import datetime

router = APIRouter()

# Set the base path where historical data will be saved
HISTORICAL_DATA_PATH = os.path.join("data", "historical", "devices")

@router.post("/start-stream/{device_id}")
async def start_stream(device_id: str, background_tasks: BackgroundTasks):
    """
    Starts streaming data for the device using its schema. Data is streamed to a Kafka topic.
    """
    # Step 1: Retrieve the device schema
    try:
        device_schema = await get_device_schema(device_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    # Step 2: Start a Kafka topic for the device
    try:
        start_kafka_stream(device_id)  # Assuming a Kafka topic is created with device ID
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start Kafka stream: {e}")

    # Step 3: Stream data using Kafka (dummy data for this example)
    background_tasks.add_task(stream_data_to_kafka, device_id, device_schema["schema"])

    return {"message": f"Streaming started for device '{device_id}'."}


@router.post("/stop-stream/{device_id}")
async def stop_stream(device_id: str):
    """
    Stops the data stream and saves all historical data for the device to a file.
    """
    # Step 1: Stop Kafka streaming for the device
    try:
        data_stream = stop_kafka_stream(device_id)  # This should return the data that was streamed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop Kafka stream: {e}")
    
    # Step 2: Save the historical data to the correct location
    try:
        save_historical_data(device_id, data_stream)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save historical data: {e}")

    return {"message": f"Streaming stopped and data saved for device '{device_id}'."}


def stream_data_to_kafka(device_id: str, schema: dict):
    """
    Continuously stream data to Kafka based on the provided schema. (Simulate streaming here).
    This function should be executed in the background.
    """
    try:
        while True:
            # Example: Generate dummy data matching the schema and send to Kafka
            data = generate_dummy_data(schema)
            send_to_kafka(device_id, data)  # Stream data to the Kafka topic
    except Exception as e:
        print(f"Error streaming data for device '{device_id}': {e}")


def generate_dummy_data(schema: dict) -> dict:
    """
    Generate dummy data based on the device schema. Simulating sensor data here.
    """
    import random
    data = {}
    for field, data_type in schema.items():
        if data_type == "float":
            data[field] = round(random.uniform(20.0, 100.0), 2)  # Random float
        elif data_type == "string":
            data[field] = datetime.now().isoformat()  # Use ISO format timestamp
    return data


def save_historical_data(device_id: str, data_stream: list):
    """
    Save the historical data for the device in a file under data/historical/devices/device_name.json.
    """
    # Ensure the historical directory exists
    device_data_path = os.path.join(HISTORICAL_DATA_PATH, f"{device_id}.json")
    create_folder(os.path.dirname(device_data_path))

    # Save the data stream to the JSON file
    save_json_file(device_data_path, {"data": data_stream})
