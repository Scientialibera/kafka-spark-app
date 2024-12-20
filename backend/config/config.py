import os

# Update default values to use Docker network service names
def is_running_in_docker():
    """Check if the application is running in a Docker container."""
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read()
    except FileNotFoundError:
        return False

# Set KAFKA_BROKER_URL based on environment
if is_running_in_docker():
    KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka:9092")  # Use Docker hostname
    SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")  # Use Docker hostname
    HADOOP_URL = os.getenv("HADOOP_URL", "hdfs://hadoop:9000")  # Consistent with the others
else:
    KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")  # Local setup
    SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "local[*]")  # Local setup
    HADOOP_URL = os.getenv("HADOOP_URL", "hdfs://localhost:9000")  # Local setup


MAX_WORKERS = int(os.getenv("MAX_WORKERS", 16))

SPARK_APP_NAME = os.getenv("SPARK_APP_NAME", "Kafka Streaming Stats")

HISTORICAL_DATA_PATH = os.getenv("HISTORICAL_DATA_PATH", "backend/data/historical/devices")
SCHEMA_DATA_PATH = os.getenv("HISTORICAL_DATA_PATH", "backend/data/device_schemas")