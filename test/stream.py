import datetime
import json 
import requests
import random
import websockets
from fastapi import APIRouter

BASE_URL = "http://localhost:8000"
WS_BASE_URL = BASE_URL.replace("http", "ws")
STREAM_TEST_ENDPOINT: str = "/test"
MAX_STR_LEN = 3

router = APIRouter()

def check_if_device_exists(name):

    url = BASE_URL + "/devices/" + name

    response = requests.get(url)
    status = response.status_code
    
    if status == 200:
        return True
    else:
        return False

def create_device(num):

    strnum = generate_string("gps_", num)

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
        
        url = BASE_URL + "/register-device"

        # Send a POST request with the JSON payload
        response = requests.post(url, json=payload)

        # Print the status code and response
        print(f"Request: {payload}")
        print(f"Status Code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
    else:
        return
    

def generate_padded_string(prefix, num):
    numstr = str(num)
    numlen = len(numstr)
    strnum = prefix + ("0" * (MAX_STR_LEN - numlen)) + numstr
    return strnum

def generate_string(prefix, num):
    numstr = str(num)
    strnum = prefix + numstr
    return strnum

async def create_test_data(device_id, num):
    run_id = generate_padded_string("run_", num)
    now = datetime.datetime.now()
    url = WS_BASE_URL + "/send-stream/"+ device_id +"/"+ run_id
    async with websockets.connect(url) as websocket:
        payload = {
            "latitude": 48.83816 + pow(-1, num) * (random.randrange(1, 1000, 1) * 0.001),
            "longitude": 2.25183 + pow(-1, num+1) * (random.randrange(1, 1000, 1) * 0.001),
            "timestamp": str(now)
        }
    
        # Convert data to JSON string
        data_str = json.dumps(payload)

        # Send data over WebSocket
        await websocket.send(data_str)
        print(f"Sent data from {device_id} (run {run_id}):  {data_str}")

        websocket.close()
    

@router.get(STREAM_TEST_ENDPOINT)
def send_test_stream():
    for player in range(1, 21, 1):
        device_id = generate_string("gps_", player)
        create_device(player)
        for i in range(1, 11, 1):
            create_test_data(device_id, i)
