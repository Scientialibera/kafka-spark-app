"""
Kafka producer and consumer utilities for streaming data.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

from aiokafka import AIOKafkaConsumer
from fastapi import HTTPException
from kafka import KafkaProducer

from backend.config.config import KAFKA_BROKER_URL
from utils.file_management import kafka_topic_name

logger = logging.getLogger(__name__)


class KafkaProducerWrapper:
    """
    Wrapper class for Kafka producer with JSON serialization.
    
    Provides a simplified interface for sending JSON data to Kafka topics.
    """
    
    def __init__(self, bootstrap_servers: str = KAFKA_BROKER_URL):
        """
        Initialize the Kafka producer.
        
        Args:
            bootstrap_servers: Kafka broker connection string
        """
        self._bootstrap_servers = bootstrap_servers
        self._producer: Optional[KafkaProducer] = None
    
    @property
    def producer(self) -> KafkaProducer:
        """Lazy initialization of Kafka producer."""
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        return self._producer

    def send(self, topic: str, value: Dict[str, Any]) -> None:
        """
        Send a message to a Kafka topic.
        
        Args:
            topic: Target Kafka topic
            value: Dictionary to send as JSON
        """
        self.producer.send(topic, value=value)

    def flush(self) -> None:
        """Flush all pending messages to Kafka."""
        if self._producer is not None:
            self._producer.flush()

    def close(self) -> None:
        """Close the Kafka producer connection."""
        if self._producer is not None:
            self._producer.close()
            self._producer = None


def send_data_to_kafka(
    producer: KafkaProducerWrapper,
    topic: str,
    data: Dict[str, Any]
) -> None:
    """
    Send data to Kafka using the provided producer.
    
    Args:
        producer: KafkaProducerWrapper instance
        topic: Target Kafka topic
        data: Data dictionary to send
    """
    producer.send(topic, value=data)


async def get_kafka_messages(
    device_id: str,
    run_id: str,
    schema_fields: Dict[str, str],
    limit: Optional[int] = None,
    timeout_seconds: int = 5
) -> List[Dict[str, Union[str, int, float, bool]]]:
    """
    Asynchronously read messages from a Kafka topic.
    
    Retrieves up to 'limit' latest messages with a configurable timeout.
    
    Args:
        device_id: The device identifier
        run_id: The run identifier
        schema_fields: Schema definition for message validation
        limit: Maximum number of messages to retrieve
        timeout_seconds: Timeout in seconds for waiting for messages
        
    Returns:
        List of message dictionaries
        
    Raises:
        HTTPException: If an error occurs reading from Kafka
    """
    topic = kafka_topic_name(device_id, run_id)
    
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
    
    # Default limit if not specified
    if limit is None:
        limit = 100

    try:
        while len(messages) < limit:
            try:
                message = await asyncio.wait_for(
                    consumer.getone(),
                    timeout=timeout_seconds
                )
                value = message.value

                # Validate message schema
                if set(value.keys()) != set(schema_fields.keys()):
                    logger.warning(
                        f"Invalid message schema for topic {topic}: {value}"
                    )
                    continue

                messages.append(value)

            except asyncio.TimeoutError:
                # Return messages gathered so far on timeout
                break

        return messages

    except Exception as e:
        logger.error(f"Error reading from Kafka topic {topic}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading from Kafka topic: {str(e)}"
        )

    finally:
        await consumer.stop()

