from kafka import KafkaProducer, KafkaConsumer

producer = None
streams = {}

def start_kafka_stream(device_id: str):
    """Starts Kafka stream by creating a Kafka topic for the device."""
    global producer
    if not producer:
        producer = KafkaProducer(bootstrap_servers='localhost:9092')
    streams[device_id] = []  # Initialize stream buffer for the device


def stop_kafka_stream(device_id: str) -> list:
    """Stops Kafka stream and returns the data that was streamed."""
    if device_id in streams:
        data_stream = streams.pop(device_id)
        return data_stream
    else:
        raise Exception(f"No active stream found for device '{device_id}'")


def send_to_kafka(device_id: str, data: dict):
    """Send data to Kafka for the device."""
    if device_id not in streams:
        raise Exception(f"No active stream found for device '{device_id}'")
    
    # Append data to the in-memory stream
    streams[device_id].append(data)

    # Simulate Kafka sending (can actually send to a Kafka topic here)
    print(f"Sent to Kafka (topic: {device_id}): {data}")
