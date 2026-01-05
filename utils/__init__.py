"""
Utilities module for Sports Prophet application.

This module provides utility functions for:
- File management and JSON handling
- Kafka producer/consumer operations
- Mathematical calculations for sports analytics
- Spark processing utilities
"""
from utils.file_management import (
    create_folder,
    device_exists,
    kafka_topic_name,
    load_json_file,
    save_json_file,
    validate_data,
    validate_schema_not_empty,
)
from utils.maths_functions import (
    calculate_acceleration_from_messages,
    calculate_speed_from_messages,
    calculate_speed_from_points,
    haversine_distance,
    parse_timestamp,
)
from utils.kafka_producer import (
    KafkaProducerWrapper,
    get_kafka_messages,
    send_data_to_kafka,
)

__all__ = [
    # File management
    "create_folder",
    "device_exists",
    "kafka_topic_name",
    "load_json_file",
    "save_json_file",
    "validate_data",
    "validate_schema_not_empty",
    # Maths
    "calculate_acceleration_from_messages",
    "calculate_speed_from_messages",
    "calculate_speed_from_points",
    "haversine_distance",
    "parse_timestamp",
    # Kafka
    "KafkaProducerWrapper",
    "get_kafka_messages",
    "send_data_to_kafka",
]