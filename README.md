# Sports Prophet

Sports Prophet is a full-stack application designed to analyze soccer match data in real-time and ad-hoc. It ingests sensor streams from devices into Kafka topics and uses Spark for real-time aggregation or direct querying for on-demand data. Users can also manage sensor schemas through the API.


### Key Directories and Files

1. **backend**: Contains the API implementation using FastAPI, Kafka integration, and Spark processing logic.
   - **api**: Holds individual API route files (`get_live_stats.py`, `register_device.py`, etc.).
   - **config**: Configuration files, including environment settings.
   - **models**: Data models and schemas for validating requests. (For device registration only.)
   - **app.py**: Main entry point for the FastAPI application.
   - **Dockerfile**: Docker setup for the backend service.
   - **requirements.txt**: Python dependencies for the backend.

2. **data**: Stores device schemas and historical data files used for sensor simulations and validations.

3. **frontend**: React-based user interface for interacting with the application.

4. **simulator-data**: Mock data files used to simulate sensor data ingestion.

5. **spark**: Spark setup files and Docker configuration for processing Kafka streams.

6. **test**: Contains unit and integration tests for backend components.

7. **utils**: Utility scripts for Kafka management, file operations, and Spark stream processing.


## Docker Details

The Sports Prophet application utilizes Docker and Docker Compose to manage and orchestrate its services. 
Below is a breakdown of each service and instructions to manage them.

### Docker Services Overview

1. **zookeeper**: A service for managing Kafka metadata and synchronization. Exposes port `2181`.
2. **kafka**: Message broker for sensor data ingestion, connected to Zookeeper. Exposes port `9092`.
3. **spark-master**: Master node for Spark processing tasks, managing worker nodes and job scheduling. Ports `7077` and `8080` are open.
4. **spark-worker**: Worker node that connects to Spark Master, processing tasks as assigned.
5. **hadoop**: Manages HDFS storage, which Spark may utilize for persistent storage. Ports `9870` (Namenode UI) and `9000` (for HDFS communication) are exposed.
6. **api**: The FastAPI-based backend application providing APIs for data access and management. Accessible on port `8000`.

### Common Docker Commands

1. **Start Services**: 
   ```
   docker-compose up -d
   ```
   This command launches all services in detached mode.

2. **Check Running Containers**: 
   ```
   docker ps
   ```
   Displays all active containers along with their names, ports, and statuses.

3. **View Logs for a Specific Container**: 
   ```
   docker logs <container_name>
   ```
   Replace `<container_name>` with the name of the container (e.g., `api`, `kafka`, etc.) to view its logs.

4. **Stop Services**: 
   ```
   docker-compose down
   ```
   Stops and removes all services defined in the `docker-compose.yml` file.

5. **Rebuild a Specific Service** (useful after code updates):
   ```
   docker-compose build <service_name>
   ```
   Replace `<service_name>` with the service you wish to rebuild, such as `api`.

### Docker Networking

All services are connected to a shared network, `kafka_network` for communication between Kafka, Zookeeper, Spark, and the API service.

## API Documentation

### 1. **Live Stats API** (`get_live_stats.py`)

#### Endpoints:

- **`POST /start-stream/{device_id}/{run_id}`**  
  Initiates a streaming job for a specific device and run.  
  **Parameters**:
  - `device_id` (str): The ID of the device.
  - `run_id` (str): The ID of the run.
  - `triggers` (dict): Dictionary with column names and min/max values to filter.
  - `window_seconds` (int): Window duration in seconds for aggregations.
  - `table_preappend` (Optional[str]): Prefix for naming the streaming view.

- **`GET /get-latest-stats/{device_id}/{run_id}`**  
  Retrieves the latest statistics from the streaming data for a given device and run.  
  **Parameters**:
  - `device_id` (str): The ID of the device.
  - `run_id` (str): The ID of the run.
  - `query` (str): SQL query to filter/select data from the streaming view.
  - `table_preappend` (Optional[str]): Prefix for the streaming view name.

- **`GET /get-stats/{device_id}/{run_id}`**  
  Fetches aggregated statistics for a given device and run.  
  **Parameters**:
  - `device_id` (str): The ID of the device.
  - `run_id` (str): The ID of the run.
  - `agg_type` (str): Type of aggregation (average, max, min, sum).

- **`GET /get-speed/{device_id}/{run_id}`**
  Retrieves the instantaneous speed for a specific device and run using the most recent two messages from Kafka.  
  **Parameters**:
  - `device_id` (str): The ID of the device.
  - `run_id` (str): The ID of the run.

### 2. **Kafka Topics API** (`kafka_topics.py`)

#### Endpoints:

- **`GET /get-topic-messages/{device_id}/{run_id}`**  
  Asynchronously retrieves Kafka messages for a given device and run. Optionally, limits the number of messages.  
  **Parameters**:
  - `device_id` (str): Device ID.
  - `run_id` (str): Run ID.
  - `limit` (Optional[int]): Maximum number of messages to retrieve.

- **`DELETE /delete-topic/{device_id}/{run_id}`**  
  Deletes a Kafka topic associated with a device and run.  
  **Parameters**:
  - `device_id` (str): Device ID.
  - `run_id` (str): Run ID.

- **`DELETE /delete-all-topics`**  
  Deletes all Kafka topics in the cluster.

- **`GET /list-topics`**  
  Deletes all Kafka topics in the cluster.

### 3. **Device Management API** (`register_device.py`)

#### Endpoints:

- **`POST /register-device`**  
  Registers a new device schema for schema consistency and directory setup.  
  **Parameters**:
  - `device` (RegisterDeviceRequest): Details and schema of the new device.

- **`PUT /update-device`**  
  Updates the schema of an existing device.  
  **Parameters**:
  - `device` (RegisterDeviceRequest): Updated device details and schema.

- **`DELETE /delete-device/{device_id}`**  
  Deletes the schema of a specified device.  
  **Parameters**:
  - `device_id` (str): Device ID to delete.

- **`GET /devices`**  
  Retrieves all registered device names.

- **`GET /device/{device_id}`**  
  Fetches the schema of a specified device.  
  **Parameters**:
  - `device_id` (str): Device ID to retrieve.

### 4. **Data Stream API** (`send_stream.py`)

#### Endpoints:

- **`/send-stream/{device_id}/{run_id}`** (WebSocket)
  Initiates a WebSocket connection to send a continuous data stream for a specific device and run. The data received through the WebSocket is validated and sent to Kafka in real-time. When the websocket disconnects, data is saved in path of choice.
  **Parameters**:
  - `device_id` (str): Unique identifier for the device sending data.
  - `run_id` (str): Identifier for the specific run associated with the device.

## Technologies Used

- **FastAPI**: Backend framework for building APIs.
- **Kafka**: Message broker for streaming sensor data.
- **Spark**: Real-time data processing engine for aggregating and querying streaming data.
- **React**: Frontend library for building user interfaces.
- **Docker**: Containerization of services for deployment and scalability.

## How to Run

1. Clone the repository and navigate to the project root.
2. Ensure Docker and Docker Compose are installed.
3. Run the backend and frontend services using Docker Compose:
docker-compose up --build
4. Access the API at `http://localhost:8000/docs` for API documentation and testing.

## Future Enhancements

- Add more device types and support for additional streaming data formats.
- Implement user authentication and authorization mechanisms.
- Expand frontend capabilities to visualize live data and historical trends interactively.

## Examples

## 1. Generating Dummy Data for Streaming

```python
import asyncio
import websockets
import json
import random
import time
from datetime import datetime

# Define the WebSocket URL with placeholders for device_id and run_id
WEBSOCKET_ENDPOINT_TEMPLATE = "ws://localhost:8000/send-stream/{device_id}/{run_id}"

DURATION_SECONDS = 120  # Total duration to send data
INTERVAL_SECONDS = 0.5  # Interval between data sends

# Approximate GPS boundaries of a football pitch
PITCH_LAT_MIN = 40.0   # Adjust this to your base latitude for the pitch
PITCH_LAT_MAX = 40.0009  # Approx 100m in latitudinal degrees
PITCH_LON_MIN = -75.0012  # Adjust this to your base longitude for the pitch
PITCH_LON_MAX = -75.0  # Approx 64m in longitudinal degrees

# Random walk step size in degrees (roughly corresponds to 1 meter)
STEP_SIZE_LAT = 0.00001  # Latitude step size for each movement (0.00001 ~ 1 meter)
STEP_SIZE_LON = 0.000015  # Longitude step size for each movement (slightly larger for more movement)

def random_walk(current_lat, current_lon):
    """Perform a random walk within the boundaries of the football pitch."""
    # Randomly adjust latitude and longitude within step size limits
    new_lat = current_lat + random.uniform(-STEP_SIZE_LAT, STEP_SIZE_LAT)
    new_lon = current_lon + random.uniform(-STEP_SIZE_LON, STEP_SIZE_LON)

    # Ensure the new position stays within the pitch boundaries
    new_lat = max(min(new_lat, PITCH_LAT_MAX), PITCH_LAT_MIN)
    new_lon = max(min(new_lon, PITCH_LON_MAX), PITCH_LON_MIN)

    return new_lat, new_lon

async def send_synthetic_data(device_id, run_id):
    # Format the WebSocket endpoint with the actual device_id and run_id
    websocket_endpoint = WEBSOCKET_ENDPOINT_TEMPLATE.format(device_id=device_id, run_id=run_id)

    async with websockets.connect(websocket_endpoint) as websocket:
        start_time = time.time()  # Use time.time() to get the current time in seconds
        end_time = start_time + DURATION_SECONDS  # Calculate the end time

        # Initialize the starting position at the center of the pitch
        current_lat = (PITCH_LAT_MIN + PITCH_LAT_MAX) / 2
        current_lon = (PITCH_LON_MIN + PITCH_LON_MAX) / 2

        while time.time() < end_time:
            # Perform a random walk to simulate movement
            current_lat, current_lon = random_walk(current_lat, current_lon)

            # Generate synthetic data matching the schema, with high precision
            data = {
                    "latitude": round(current_lat, 6),   # Ensure precision of 6 decimal places, remains as float
                    "longitude": round(current_lon, 6),  # Ensure precision of 6 decimal places, remains as float
                    "timestamp": datetime.utcnow().isoformat()  # ISO format timestamp remains as string
                }

            # Convert data to JSON string
            data_str = json.dumps(data)

            # Send data over WebSocket
            await websocket.send(data_str)
            print(f"Sent data from {device_id} (run {run_id}): {data_str}")

            # Wait for the specified interval before sending the next message
            await asyncio.sleep(INTERVAL_SECONDS)

async def main():
    # Create different run_id values for each task
    run_ids = ["run_001", "run_002", "run_003", "run_004", "run_005"]

    # Run multiple concurrent WebSocket connections for gps, each with a different run_id
    tasks = [
        send_synthetic_data("gps_1", run_id)
        for run_id in run_ids
    ]
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)

# Run the main function
await main()
```

## 2. Adding Devices

```python
import requests

# Define the URL of the FastAPI endpoint
url = "http://127.0.0.1:8000/register-device"

# Define the payload (device registration details)
payload = {
    "device_name": "sensor_002",
    "schema": {
        "temperature": "float",
        "humidity": "float",
        "timestamp": "string"
    }
}

# Send a POST request with the JSON payload
response = requests.post(url, json=payload)

# Print the status code and response
print(f"Status Code: {response.status_code}")
print(f"Response JSON: {response.json()}")
```

## 3. Spark Processing Aggregation (Inception-to-Date)

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define the base FastAPI endpoint template
url_template = "http://localhost:8000/get-stats/{device_id}/{run_id}"

# Define the sensors, runs, and aggregation types you want to check
sensor = "gps_1"
runs = ["run_001", "run_002", "run_003", "run_004", "run_005"]
aggregation_types = ["average", "max"]  # Add more as needed (e.g., "min", "sum")

# Function to make the GET request and process the response
def check_run(device_id, run_id, agg_type):
    # Format the URL and add the aggregation type as a query parameter
    url = url_template.format(device_id=device_id, run_id=run_id) + f"?agg_type={agg_type}"
    try:
        # Make the GET request to the FastAPI endpoint
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Print the response from the server
            return f"Success for {device_id}/{run_id} with {agg_type}: {response.json()}"
        else:
            return f"Failed for {device_id}/{run_id} with {agg_type}, status code: {response.status_code}, {response.text}"
    except Exception as e:
        return f"An error occurred for {device_id}/{run_id} with {agg_type}: {e}"

# Main function to handle concurrent requests
def main():
    # Use ThreadPoolExecutor to run requests concurrently
    with ThreadPoolExecutor(max_workers=9) as executor:
        # Submit tasks to the executor for each sensor, run, and aggregation type combination
        futures = {
            executor.submit(check_run, sensor, run, agg_type): (run, agg_type)
            for run in runs for agg_type in aggregation_types
        }
        
        # Process the results as they complete
        for future in as_completed(futures):
            try:
                result = future.result()
                print(result)
            except Exception as exc:
                run, agg_type = futures[future]
                print(f"An error occurred for {sensor}/{run} with {agg_type}: {exc}")

# Run the main function
if __name__ == "__main__":
    main()
```

## 4. Fetching Latest Kafka Topic Messages

```python
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define the sensors and runs you want to check
sensor = "gps_1"
runs = ["run_001", "run_002", "run_003", "run_004", "run_005"]
limit = 1  # Fetch the latest messages with this limit
base_url = "http://127.0.0.1:8000/get-topic-messages/{device_id}/{run_id}?limit={limit}"

# Function to make the request and process the response
def fetch_kafka_messages(device_id, run_id, limit):
    url = base_url.format(device_id=device_id, run_id=run_id, limit=limit)
    try:
        # Make the request to the FastAPI endpoint
        response = requests.get(url)
        # Check the status of the response
        if response.status_code == 200:
            response_json = response.json()
            print(f"Response for {device_id}/{run_id}:", json.dumps(response_json, indent=4))
            # Get the actual messages returned (if any)
            messages = response_json.get('messages', [])
            if messages:
                print(f"Latest Message for {device_id}/{run_id}:", json.dumps(messages[0], indent=4))
            else:
                print(f"No messages returned for {device_id}/{run_id}.")
        else:
            print(f"Error for {device_id}/{run_id}: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred for {device_id}/{run_id}: {e}")

# Main function to run the requests concurrently
def main():
    # Use ThreadPoolExecutor to run requests concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit tasks to the executor for each sensor and run combination
        futures = [executor.submit(fetch_kafka_messages, sensor, run, limit) for run in runs]
        
        # Process the results as they complete
        for future in as_completed(futures):
            try:
                future.result()  # This will raise any exception from the fetch_kafka_messages function
            except Exception as exc:
                print(f"An error occurred: {exc}")

# Run the main function
if __name__ == "__main__":
    main()
```

## 5. Starting Spark Processing and Querying Temporary View

```python
import aiohttp
import asyncio

# Define the base FastAPI endpoint templates
start_stream_url_template = "http://localhost:8000/start-stream/{device_id}/{run_id}"
get_latest_stats_url_template = "http://localhost:8000/get-latest-stats/{device_id}/{run_id}"

# Example triggers
triggers = {
    "latitude": [39.0, 40.1],  # Min and max threshold for latitude
    "longitude": [-75.0, -70.0],  # Min and max threshold for longitude
}

# Asynchronous function to start the stream for a device and run
async def start_stream(device_id, run_id, triggers):
    url = start_stream_url_template.format(device_id=device_id, run_id=run_id)
    async with aiohttp.ClientSession() as session:
        try:
            # Make the POST request to the start-stream endpoint
            async with session.post(url, json={"triggers": triggers, "window_seconds": 2, "table_preappend": "threshold"}) as response:
                if response.status == 200:
                    print(f"Stream started successfully for {device_id}/{run_id}")
                else:
                    text = await response.text()
                    print(f"Failed to start stream for {device_id}/{run_id} with status code: {response.status}, {text}")
        except Exception as e:
            print(f"An error occurred while starting the stream for {device_id}/{run_id}: {e}")

# Asynchronous function to get the latest stats for a device and run
async def check_latest_stats(device_id, run_id):
    url = get_latest_stats_url_template.format(device_id=device_id, run_id=run_id)
    async with aiohttp.ClientSession() as session:
        try:
            # Make the GET request to the get-latest-stats endpoint
            # Adjust the query to fetch only the latest row
            query = "SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 1"
            params = {"query": query, "table_preappend": "threshold"}
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"Success for {device_id}/{run_id}: {data}")
                else:
                    text = await response.text()
                    print(f"Failed for {device_id}/{run_id} with status code: {response.status}, {text}")
        except Exception as e:
            print(f"An error occurred for {device_id}/{run_id}: {e}")

# Main asynchronous function to handle the test request for streaming latest stats
async def main_streaming_test():
    # Define run_ids
    run_ids = ["run_001", "run_002", "run_003", "run_004", "run_005"]
    
    # Step 1: Start all streams concurrently
    start_tasks = [start_stream("gps_1", run_id, triggers) for run_id in run_ids]
    await asyncio.gather(*start_tasks)
    
    # Step 2: Wait for streams to stabilize (e.g., a few seconds if needed)
    await asyncio.sleep(0)  # Adjust the sleep duration based on your streaming setup
    
    # Step 3: Query the latest stats concurrently
    query_tasks = [check_latest_stats("gps_1", run_id) for run_id in run_ids]
    await asyncio.gather(*query_tasks)

# Run the main_streaming_test function
await main_streaming_test()
```

## 6. Getting Instant Speed

```python
import aiohttp
import asyncio

# Define the FastAPI endpoint template for the get_speed endpoint
get_speed_url_template = "http://localhost:8000/get-speed/{device_id}/{run_id}"

# Asynchronous function to test the get-speed endpoint
async def test_get_speed(device_id, run_id):
    url = get_speed_url_template.format(device_id=device_id, run_id=run_id)
    async with aiohttp.ClientSession() as session:
        try:
            # Make the GET request to the get-speed endpoint
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Validate that the response contains the expected fields
                    if "device_id" in data and "run_id" in data and "speed" in data:
                        print(f"Success for {device_id}/{run_id}: {data}")
                    else:
                        print(f"Unexpected response structure for {device_id}/{run_id}: {data}")
                else:
                    text = await response.text()
                    print(f"Failed for {device_id}/{run_id} with status code: {response.status}, {text}")
        except Exception as e:
            print(f"An error occurred for {device_id}/{run_id}: {e}")

# Main asynchronous function to handle the test requests for multiple device and run combinations
async def main_get_speed_test():
    # Define run_ids and corresponding device_ids
    test_cases = [
        {"device_id": "gps_1", "run_id": "run_001"},
        {"device_id": "gps_1", "run_id": "run_002"},
        {"device_id": "gps_1", "run_id": "run_003"},
        {"device_id": "gps_1", "run_id": "run_004"},
        {"device_id": "gps_1", "run_id": "run_005"},
    ]

    # Create tasks to test each device_id and run_id pair concurrently
    test_tasks = [test_get_speed(case["device_id"], case["run_id"]) for case in test_cases]
    
    # Run all tasks concurrently
    await asyncio.gather(*test_tasks)

# Run the main_get_speed_test function
await main_get_speed_test()
```