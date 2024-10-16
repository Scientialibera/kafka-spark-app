import json
import os
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from utils.file_management import device_exists
from confluent_kafka.admin import AdminClient
from aiokafka import AIOKafkaConsumer
import asyncio

router = APIRouter()

SCHEMA_SAVE_PATH = os.path.join("data", "device_schemas")
KAFKA_BROKER_URL = 'localhost:9092'  # Kafka broker URL

# Kafka Admin client
admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKER_URL})

async def get_kafka_messages(device_id: str, run_id: str, schema_fields: dict, limit: Optional[int] = None):
    """
    Asynchronously reads messages from the Kafka topic corresponding to the device_id and run_id.
    Retrieves only the latest message(s) without maintaining a bookmark in Kafka, with a 5-second timeout if no new messages.
    """
    topic = f"{device_id}_{run_id}"

    # Create a new Kafka consumer, starting from the latest message and not committing offsets
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='latest',  # Always start from the latest message
        enable_auto_commit=False,    # Do not commit offsets
        group_id=None,               # No group, so offsets are not tracked by Kafka
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    await consumer.start()
    messages = []
    timeout_seconds = 5  # Timeout of 5 seconds

    try:
        # Try to get a message within the timeout period
        try:
            message = await asyncio.wait_for(consumer.getone(), timeout=timeout_seconds)
            value = message.value

            # Validate message against schema_fields
            if set(value.keys()) != set(schema_fields.keys()):
                raise ValueError(f"Invalid message schema for message: {value}")

            # Append the latest message to the results list
            messages.append(value)

        except asyncio.TimeoutError:
            # Timeout after 5 seconds
            return {"message": "No new data", "device_id": device_id, "run_id": run_id}

        # Return the message if retrieved
        return messages

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading from Kafka topic: {str(e)}")
    finally:
        await consumer.stop()


@router.get("/get-topic-messages/{device_id}/{run_id}")
async def get_topic_messages(device_id: str, run_id: str, limit: Optional[int] = Query(None)):
    """
    Endpoint to asynchronously retrieve Kafka messages for a given device_id and run_id.
    If 'limit' is provided, it limits the number of messages retrieved.
    """
    try:
        # Retrieve the device schema
        device_schema = device_exists(SCHEMA_SAVE_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]
        
        # Fetch messages from the Kafka topic with optional limit
        messages = await get_kafka_messages(device_id, run_id, schema_fields, limit)
        
        return {"device_id": device_id, "run_id": run_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")

@router.delete("/delete-topic/{device_id}/{run_id}")
async def delete_topic_by_device_name(device_id: str, run_id: str):
    """
    Endpoint to delete a Kafka topic based on the device_id and run_id.
    """
    topic = f"{device_id}_{run_id}"
    try:
        # Delete the topic using Kafka AdminClient
        future = admin_client.delete_topics([topic])
        result = future[topic].result()  # Wait for the deletion result

        if result is None:
            return {"message": f"Topic {topic} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete topic: {str(e)}")


@router.delete("/delete-all-topics")
async def delete_all_topics():
    """
    Endpoint to delete all Kafka topics in the cluster.
    """
    try:
        # Get the list of all topics
        metadata = admin_client.list_topics(timeout=10)
        topics = list(metadata.topics.keys())

        # Delete all topics
        future = admin_client.delete_topics(topics)
        results = {topic: future[topic].result() for topic in topics}

        return {"message": "All topics deleted successfully", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete all topics: {str(e)}")
