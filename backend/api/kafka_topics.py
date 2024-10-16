import json
import os

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from utils.file_management import device_exists

router = APIRouter()

SCHEMA_SAVE_PATH = os.path.join("data", "device_schemas")

# Kafka consumer settings
KAFKA_BROKER_URL = 'localhost:9092'  # Kafka broker URL

from aiokafka import AIOKafkaConsumer

async def get_kafka_messages(device_id: str, run_id: str, schema_fields: dict, limit: Optional[int] = None):
    """
    Asynchronously reads messages from the Kafka topic corresponding to the device_id and run_id.
    Validates the messages according to the schema_fields.
    Retrieves messages in reverse order (latest to earliest) with a specified limit.
    If no limit is provided, fetches all available messages.
    """
    topic = f"{device_id}_{run_id}"
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id=f"{device_id}_group",
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    await consumer.start()
    messages = []

    try:
        async for message in consumer:
            value = message.value

            # Validate message against schema_fields
            if set(value.keys()) != set(schema_fields.keys()):
                raise ValueError(f"Invalid message schema for message: {value}")

            # If valid, append the message to the results list
            messages.append(value)

            # If a limit is specified and reached, stop
            if limit is not None and len(messages) >= limit:
                break

        # Return messages in reverse order (latest to earliest)
        return list(reversed(messages))
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
