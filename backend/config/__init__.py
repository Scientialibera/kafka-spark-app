"""
Backend configuration module.

This module exports configuration settings, constants, and logging utilities.
"""
from backend.config.config import (
    KAFKA_BROKER_URL,
    SPARK_MASTER_URL,
    SPARK_APP_NAME,
    HADOOP_URL,
    MAX_WORKERS,
    HISTORICAL_DATA_PATH,
    SCHEMA_DATA_PATH,
    API_HOST,
    API_PORT,
    CORS_ORIGINS,
)
from backend.config.logging_config import logger, setup_logging

__all__ = [
    "KAFKA_BROKER_URL",
    "SPARK_MASTER_URL",
    "SPARK_APP_NAME",
    "HADOOP_URL",
    "MAX_WORKERS",
    "HISTORICAL_DATA_PATH",
    "SCHEMA_DATA_PATH",
    "API_HOST",
    "API_PORT",
    "CORS_ORIGINS",
    "logger",
    "setup_logging",
]
