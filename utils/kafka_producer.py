import json
import asyncio
from typing import Optional, List, Dict, Union

from fastapi import HTTPException
from aiokafka import AIOKafkaConsumer
from kafka import KafkaProducer

from backend.config.config import KAFKA_BROKER_URL
from utils.file_management import kafka_topic_name

async def get_kafka_messages(
    device_id: str,
    run_id: str,
    schema_fields: Dict[str, Union[type, str]],
    limit: Optional[int] = None
) -> Union[List[Dict[str, Union[str, int, float, bool]]], Dict[str, str]]:
    """
    Asynchronously reads messages from the Kafka topic corresponding to the device_id and run_id.
    Retrieves up to 'limit' latest messages with a 5-second timeout if no new messages.

    Args:
        device_id (str): The ID of the device.
        run_id (str): The ID of the run associated with the device.
        schema_fields (Dict[str, Union[type, str]]): A dictionary representing the schema fields of the messages.
        limit (Optional[int], optional): The maximum number of messages to retrieve. Defaults to None.

    Returns:
        Union[List[Dict[str, Union[str, int, float, bool]]], Dict[str, str]]: 
        A list of messages if successful, or a message indicating no new data if timed out.
    """
    topic: str = kafka_topic_name(device_id, run_id)

    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id=None,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    await consumer.start()
    messages: List[Dict[str, Union[str, int, float, bool]]] = []
    timeout_seconds: int = 5

    try:
        while len(messages) < limit:
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=timeout_seconds)
                value = message.value

                if set(value.keys()) != set(schema_fields.keys()):
                    raise ValueError(f"Invalid message schema for message: {value}")

                messages.append(value)

            except asyncio.TimeoutError:
                # If we time out, return the messages we have gathered so far
                break

        return messages

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading from Kafka topic: {str(e)}")

    finally:
        await consumer.stop()


class KafkaProducerWrapper:
    def __init__(self, bootstrap_servers="localhost:9092"):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def send(self, topic: str, value: dict):
        self.producer.send(topic, value=value)

    def flush(self):
        self.producer.flush()

    def close(self):
        self.producer.close()


def send_data_to_kafka(producer: KafkaProducerWrapper, topic: str, data: dict):
    """
    Sends data to Kafka using the provided Kafka producer.
    """
    producer.send(topic, value=data)

