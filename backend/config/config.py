import os

# Update default values to use Docker network service names
KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "kafka:9092")
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 16))

SPARK_APP_NAME = os.getenv("SPARK_APP_NAME", "Kafka Streaming Stats")
SPARK_MASTER_URL = os.getenv("SPARK_MASTER_URL", "spark://spark-master:7077")

HADOOP_URL = os.getenv("HADOOP_URL", "hdfs://hadoop:9000")

HISTORICAL_DATA_PATH = os.getenv("HISTORICAL_DATA_PATH", "data/historical/devices")