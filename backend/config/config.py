"""
Application configuration settings.

This module provides configuration settings for Kafka, Spark, and file paths,
with automatic detection of Docker vs local environments.
"""
import os
from typing import Optional


def is_running_in_docker() -> bool:
    """
    Check if the application is running in a Docker container.
    
    Returns:
        bool: True if running in Docker, False otherwise.
    """
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read()
    except FileNotFoundError:
        return False


def get_env_var(key: str, docker_default: str, local_default: str) -> str:
    """
    Get environment variable with different defaults for Docker and local environments.
    
    Args:
        key: Environment variable name
        docker_default: Default value when running in Docker
        local_default: Default value when running locally
        
    Returns:
        The environment variable value or appropriate default
    """
    default = docker_default if is_running_in_docker() else local_default
    return os.getenv(key, default)


# =============================================================================
# Kafka Configuration
# =============================================================================

KAFKA_BROKER_URL: str = get_env_var(
    "KAFKA_BROKER_URL",
    docker_default="kafka:9092",
    local_default="localhost:9092"
)

# =============================================================================
# Spark Configuration
# =============================================================================

SPARK_MASTER_URL: str = get_env_var(
    "SPARK_MASTER_URL",
    docker_default="spark://spark-master:7077",
    local_default="local[*]"
)

SPARK_APP_NAME: str = os.getenv("SPARK_APP_NAME", "Kafka Streaming Stats")

# =============================================================================
# Hadoop Configuration
# =============================================================================

HADOOP_URL: str = get_env_var(
    "HADOOP_URL",
    docker_default="hdfs://hadoop:9000",
    local_default="hdfs://localhost:9000"
)

# =============================================================================
# Worker Configuration
# =============================================================================

MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "16"))

# =============================================================================
# File Paths
# =============================================================================

# Base paths
_BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HISTORICAL_DATA_PATH: str = os.getenv(
    "HISTORICAL_DATA_PATH",
    os.path.join(_BASE_PATH, "data", "historical", "devices")
)

SCHEMA_DATA_PATH: str = os.getenv(
    "SCHEMA_DATA_PATH",
    os.path.join(_BASE_PATH, "data", "device_schemas")
)

# =============================================================================
# API Configuration
# =============================================================================

API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "8000"))

# CORS Origins
CORS_ORIGINS: list = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
).split(",")
