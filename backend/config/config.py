import os

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9092")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 16))