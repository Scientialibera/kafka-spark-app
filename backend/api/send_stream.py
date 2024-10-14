from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from utils.kafka_producer import KafkaProducerWrapper, send_data_to_kafka
from utils.file_management import (
    create_folder,
    save_json_file,
    device_exists,
    validate_data
)
import os
import json

router = APIRouter()

SCHEMA_SAVE_PATH = os.path.join("data", "device_schemas")
HISTORICAL_DATA_PATH = os.path.join("data", "historical", "devices")
ENDPOINT_WEBSOCKET = "/send-stream/{device_id}/{run_id}"

async def process_received_data(websocket: WebSocket, device_id: str, run_id: str, data: dict, schema_fields: dict, producer: KafkaProducerWrapper, data_list: list):
    """
    Processes the data received from the WebSocket, validates it, and sends it to Kafka if valid.
    """
    # Validate the data format against the actual schema
    if not validate_data(data, schema_fields):
        # Send an error message back through WebSocket when validation fails
        await websocket.send_text("Validation failed. Data does not match the schema.")
        print(f"Validation failed for device {device_id}, run {run_id}. Data: {data}")
        return False  # Return false to stop further processing
    
    # Send data to Kafka if valid
    kafka_topic = f"{device_id}_{run_id}"
    send_data_to_kafka(producer, kafka_topic, data)

    # Collect data for historical saving
    data_list.append(data)

    return True  # Indicate successful processing

async def handle_websocket_disconnect(device_id: str, run_id: str ,data_list: list):
    """
    Handles WebSocket disconnection, including saving historical data.
    """
    # Save historical data after disconnection
    create_folder(os.path.join(HISTORICAL_DATA_PATH, device_id, run_id))
    historical_file = os.path.join(HISTORICAL_DATA_PATH, device_id, run_id, f"{device_id}.json")

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


@router.websocket(ENDPOINT_WEBSOCKET)
async def send_stream(websocket: WebSocket, device_id: str, run_id: str):
    await websocket.accept()
    data_list = []
    producer = None  # Define producer here for final cleanup in 'finally'
    
    try:
        device_schema = device_exists(SCHEMA_SAVE_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]
        producer = KafkaProducerWrapper()

        while True:
            data_text = await websocket.receive_text()
            data = json.loads(data_text)

            # Process the data and check for validation errors
            valid = await process_received_data(websocket, device_id, run_id, data, schema_fields, producer, data_list)

            if not valid:
                # If validation fails, stop further processing and close the WebSocket connection
                await websocket.send_text("Closing connection due to validation error.")
                await websocket.close(code=1003)  # Close with code indicating unsupported data
                break

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for device '{device_id}'.")
    except Exception as e:
        print(f"Error in send_stream: {e}")
        await websocket.close(code=1006)  # General error code
    finally:
        if producer:
            producer.flush()
            producer.close()
        await handle_websocket_disconnect(device_id, run_id, data_list)