import os
from typing import Optional, List, Dict, Union

from fastapi import APIRouter, HTTPException
from confluent_kafka.admin import AdminClient
import asyncio

from utils.file_management import device_exists, kafka_topic_name
from utils.kafka_producer import get_kafka_messages
from backend.config.config import KAFKA_BROKER_URL, SCHEMA_DATA_PATH

router = APIRouter()

SCHEMA_SAVE_PATH: str = SCHEMA_DATA_PATH

GET_TOPIC_MESSAGES_ENDPOINT: str = "/get-topic-messages/{device_id}/{run_id}"
GET_AVERAGE_TOPIC_MESSAGES_ENDPOINT: str = "/get-team-kafka-stats/{num_players}/{run_id}"
DELETE_TOPIC_ENDPOINT: str = "/delete-topic/{device_id}/{run_id}"
DELETE_ALL_TOPICS_ENDPOINT: str = "/delete-all-topics"
LIST_TOPICS_ENDPOINT: str = "/list-topics"


# Kafka Admin client
admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKER_URL})

@router.get(GET_TOPIC_MESSAGES_ENDPOINT)
async def get_topic_messages(
    device_id: str,
    run_id: str,
    limit: Optional[int] = None
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


@router.delete(DELETE_TOPIC_ENDPOINT)
async def delete_topic_by_device_name(device_id: str, run_id: str) -> Dict[str, str]:
    """
    Endpoint to delete a Kafka topic based on the device_id and run_id.

    Args:
        device_id (str): The ID of the device.
        run_id (str): The ID of the run associated with the device.

    Returns:
        Dict[str, str]: A message indicating the result of the topic deletion.
    """
    topic: str = kafka_topic_name(device_id, run_id)
    try:
        future = admin_client.delete_topics([topic])
        result = future[topic].result()

        if result is None:
            return {"message": f"Topic {topic} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete topic: {str(e)}")


@router.delete(DELETE_ALL_TOPICS_ENDPOINT)
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


@router.get(LIST_TOPICS_ENDPOINT)
async def list_topics() -> Dict[str, Union[str, List[str]]]:
    """
    Endpoint to retrieve all Kafka topics.

    Returns:
        Dict[str, Union[str, List[str]]]: A message and a list of all Kafka topics.
    """
    try:
        # Get metadata for all topics
        metadata = admin_client.list_topics(timeout=10)
        topics = list(metadata.topics.keys())

        return {"message": "Topics retrieved successfully", "topics": topics}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list topics: {str(e)}")


@router.get(GET_AVERAGE_TOPIC_MESSAGES_ENDPOINT)
async def get_team_kafka_stats(
    num_players: int,
    run_id: str
) -> Dict[str, Union[str, float]]:
    """
    For a given number of players and a run_id, this endpoint fetches heart_rate and temperature
    from Kafka (latest messages) and computes the team averages.

    Device IDs:
    - Heart Rate devices: "player_heart_rate_1", ..., "player_heart_rate_{num_players}" (expects field: heart_rate)
    - Temperature devices: "player_temperature_1", ..., "player_temperature_{num_players}" (expects field: temperature)

    This endpoint calls get_topic_messages(device_id, run_id, limit=1) for each device
    and aggregates the results.

    Returns a JSON with:
    {
      "run_id": "...",
      "team_average_heart_rate": ...,
      "team_average_temperature": ...
    }
    """

    heart_rate_devices = [f"player_heart_rate_{i}" for i in range(1, num_players + 1)]
    temperature_devices = [f"player_temperature_{i}" for i in range(1, num_players + 1)]

    async def fetch_latest_message(device_id: str):
        # Directly call the internal async function rather than an HTTP request
        response = await get_topic_messages(device_id, run_id, limit=1)
        messages = response.get("messages", [])
        return messages[0] if messages else None

    # Create tasks for all heart_rate and temperature devices
    tasks = [fetch_latest_message(d) for d in heart_rate_devices + temperature_devices]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Separate the results by device type
    heart_rate_results = results[0:len(heart_rate_devices)]
    temperature_results = results[len(heart_rate_devices):]

    # Extract and compute averages
    heart_rates = []
    for r in heart_rate_results:
        if isinstance(r, dict) and "heart_rate" in r:
            heart_rates.append(r["heart_rate"])

    temperatures = []
    for r in temperature_results:
        if isinstance(r, dict) and "temperature" in r:
            temperatures.append(r["temperature"])

    # Validate that we got at least some data
    if not heart_rates or not temperatures:
        raise HTTPException(status_code=500, detail="No valid heart_rate or temperature data retrieved.")

    avg_heart_rate = sum(heart_rates) / len(heart_rates)
    avg_temperature = sum(temperatures) / len(temperatures)

    return {
        "run_id": run_id,
        "team_average_heart_rate": avg_heart_rate,
        "team_average_temperature": avg_temperature
    }