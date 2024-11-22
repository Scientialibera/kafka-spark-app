from concurrent.futures import thread
import websockets
import requests
import json
import random
import time
from datetime import datetime
from fastapi import APIRouter

router = APIRouter()
# Define the WebSocket URL with placeholders for device_id and run_id
WEBSOCKET_ENDPOINT_TEMPLATE = "ws://localhost:8000/send-stream/{device_id}/{run_id}"

DURATION_SECONDS = 500  # Total duration to send data
INTERVAL_SECONDS = 0.5  # Interval between data sends
MAX_STR_LEN = 3
BASE_URL = "http://localhost:8000"
GEN_TEST_DATA_ENDPOINT = "/generate-test-data"

def generate_padded_string(schema_type, num):
    numstr = str(num)
    numlen = len(numstr)
    strnum = schema_type +"_"+ ("0" * (MAX_STR_LEN - numlen)) + numstr
    return strnum

def generate_string(schema_type, num):
    numstr = str(num)
    strnum = schema_type + "_"+ numstr
    return strnum

def generate_heart_rate():
    return random.randint(55, 150)

def check_if_device_exists(name):

    url = BASE_URL + "/devices/" + name

    response = requests.get(url)
    status = response.status_code
    
    if status == 200:
        return True
    else:
        return False

def create_device(num, schema_type):
    strnum = generate_string(schema_type, num)

    if schema_type == "gps":
        if not check_if_device_exists(strnum):
            # Define the payload (device registration details)
            payload = {
                "device_name": strnum,
                "schema": {
                    "device_name": strnum,
                    "schema": {
                        "latitude": "float",
                        "longitude": "float",
                        "timestamp": "string"
                    }
                }
            }   
    elif schema_type == "heart_rate":
        if not check_if_device_exists(strnum):
            # Define the payload (device registration details)
            payload = {
                "device_name": strnum,
                "schema": {
                    "device_name": strnum,
                    "schema": {
                        "heart_rate": "int",
                        "timestamp": "string"
                    }
                }
            }

    url = BASE_URL + "/register-device"
    # Send a POST request with the JSON payload
    response = requests.post(url, json=payload)

        # Print the status code and response
    print(f"Request: {payload}")
    print(f"Status Code: {response.status_code}")
    print(f"Response JSON: {response.json()}")

async def send_synthetic_data(device_id, run_id, schema_type):
    # Format the WebSocket endpoint with the actual device_id and run_id
    websocket_endpoint = WEBSOCKET_ENDPOINT_TEMPLATE.format(device_id=device_id, run_id=run_id)

    async with websockets.connect(websocket_endpoint) as websocket:

        # Initialize the starting position at the center of the pitch for GPS
        init_lat = 48.8413634
        init_lon = 2.2530693
        message_count = 0  # Counter to track the number of messages sent
        now = datetime.datetime.now()

        if schema_type == "gps":
            data = {
                "latitude":  round(init_lat + random.randrange(1, 1000, 1) * 0.0001 * pow(-1, message_count),7),
                "longitude": round(init_lon + random.randrange(1, 1000, 1) * 0.0001 * pow(-1, message_count), 7),
                "timestamp": str(now)
            }

        elif schema_type == "heart_rate":
            heart_rate = generate_heart_rate()
            data = {
                "heart_rate": heart_rate,
                "timestamp": str(now)
            }

            # Convert data to JSON string
            data_str = json.dumps(data)

            # Send data over WebSocket
            await websocket.send(data_str)
            print(f"Sent data from {device_id} (run {run_id}): {data_str}")

            # Increment the message count
            message_count += 1

            # Wait for the specified interval before sending the next message
            thread.sleep(INTERVAL_SECONDS)

@router.post(GEN_TEST_DATA_ENDPOINT)
def main():
    for player in range(1, 21, 1):
        create_device(player, "gps")
        create_device(player, "player_heart_rate")
        for run in range(1, 11, 1):
            run_id = generate_padded_string("run", run)
            device_id = generate_string("gps", player)
            send_synthetic_data(device_id, run_id, "gps")
            device_id = generate_string("player_heart_rate", player)
            send_synthetic_data(device_id, run_id, "player_heart_rate")
