from kafka import KafkaProducer
import json


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

