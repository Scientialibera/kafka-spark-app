import os
import json
from typing import List, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from utils.kafka_producer import KafkaProducerWrapper, send_data_to_kafka
from utils.file_management import (
    create_folder,
    save_json_file,
    device_exists,
    validate_data,
    handle_websocket_disconnect,
    process_received_data
)

router = APIRouter()

# Constants
SCHEMA_SAVE_PATH: str = os.path.join("data", "device_schemas")
ENDPOINT_WEBSOCKET: str = "/send-stream/{device_id}/{run_id}"


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



