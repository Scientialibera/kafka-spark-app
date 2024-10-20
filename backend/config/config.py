import os

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 16))
SPARK_APP_NAME = os.getenv("SPARK_APP_NAME", "Kafka Streaming Stats")