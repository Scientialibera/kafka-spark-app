import os
from typing import Optional, List, Dict, Union

from fastapi import APIRouter, HTTPException, Query
from confluent_kafka.admin import AdminClient

from utils.file_management import device_exists
from utils.kafka_producer import get_kafka_messages
from backend.config.config import KAFKA_BROKER_URL

router = APIRouter()

SCHEMA_SAVE_PATH: str = os.path.join("data", "device_schemas")


# Kafka Admin client
admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKER_URL})

@router.get("/get-topic-messages/{device_id}/{run_id}")
async def get_topic_messages(
    device_id: str,
    run_id: str,
    limit: Optional[int] = Query(None)
) -> Dict[str, Union[str, List[Dict[str, Union[str, int, float, bool]]]]]:
    """
    Endpoint to asynchronously retrieve Kafka messages for a given device_id and run_id.
    If 'limit' is provided, it limits the number of messages retrieved.

    Args:
        device_id (str): The ID of the device.
        run_id (str): The ID of the run associated with the device.
        limit (Optional[int], optional): The maximum number of messages to retrieve. Defaults to None.

    Returns:
        Dict[str, Union[str, List[Dict[str, Union[str, int, float, bool]]]]]: 
        A dictionary containing device_id, run_id, and the retrieved messages.
    """
    try:
        device_schema = device_exists(SCHEMA_SAVE_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]

        messages = await get_kafka_messages(device_id, run_id, schema_fields, limit)

        # If no messages were retrieved, return an empty list
        if not messages or not isinstance(messages, list):
            messages = []

        # Ensure each message is a dictionary with the expected types
        validated_messages = []
        for msg in messages:
            if isinstance(msg, dict):
                validated_msg = {k: v for k, v in msg.items() if isinstance(v, (str, int, float, bool))}
                validated_messages.append(validated_msg)

        response = {"device_id": device_id, "run_id": run_id, "messages": validated_messages}

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.delete("/delete-topic/{device_id}/{run_id}")
async def delete_topic_by_device_name(device_id: str, run_id: str) -> Dict[str, str]:
    """
    Endpoint to delete a Kafka topic based on the device_id and run_id.

    Args:
        device_id (str): The ID of the device.
        run_id (str): The ID of the run associated with the device.

    Returns:
        Dict[str, str]: A message indicating the result of the topic deletion.
    """
    topic: str = f"{device_id}_{run_id}"
    try:
        future = admin_client.delete_topics([topic])
        result = future[topic].result()

        if result is None:
            return {"message": f"Topic {topic} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete topic: {str(e)}")


@router.delete("/delete-all-topics")
async def delete_all_topics() -> Dict[str, Union[str, Dict[str, Optional[None]]]]:
    """
    Endpoint to delete all Kafka topics in the cluster.

    Returns:
        Dict[str, Union[str, Dict[str, Optional[None]]]]: 
        A message indicating the result of the deletion operation for each topic.
    """
    try:
        metadata = admin_client.list_topics(timeout=10)
        topics = list(metadata.topics.keys())

        future = admin_client.delete_topics(topics)
        results = {topic: future[topic].result() for topic in topics}

        return {"message": "All topics deleted successfully", "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete all topics: {str(e)}")
