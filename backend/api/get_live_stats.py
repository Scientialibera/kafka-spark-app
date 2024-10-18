from typing import Dict, List
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, Query, Body
from utils.spark_processor import get_kafka_batch_aggregates, start_streaming_aggregation, get_latest_stats
from utils.file_management import device_exists

router = APIRouter()

GET_STATS_ENDPOINT = "/get-stats/{device_id}/{run_id}"
GET_LATEST_STATS_ENDPOINT = "/get-latest-stats/{device_id}/{run_id}"
DEVICE_SCHEMA_PATH = "data/device_schemas"

# Create a ThreadPoolExecutor for concurrent Spark jobs
executor = ThreadPoolExecutor(max_workers=16)

# Generic endpoint function for getting aggregated stats
async def get_aggregated_stats(device_id: str, run_id: str, agg_type: str):
    loop = asyncio.get_event_loop()
    try:
        # Retrieve the device schema from file
        device_schema = device_exists(DEVICE_SCHEMA_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]  # Extract actual schema fields

        # Get the Kafka stream and apply dynamic aggregation (run in a thread to avoid blocking)
        kafka_topic = f"{device_id}_{run_id}"
        result = await loop.run_in_executor(executor, get_kafka_batch_aggregates, kafka_topic, schema_fields, agg_type)

        # Format the result dynamically
        response = {"device_id": device_id, "aggregation": agg_type}
        for field in schema_fields.keys():
            if schema_fields[field] in ["float", "int"]:  # Include only numeric fields in the response
                response[f"{agg_type}_{field}"] = result.get(f"{agg_type}_{field}", None)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch {agg_type} stats: {str(e)}")


# Function to start the streaming aggregation for a device
def initialize_streaming(device_id: str, run_id: str, triggers: dict, window_seconds: int = 5):
    """
    Initialize the streaming aggregation for the given device and run ID if it's not already running.
    """
    try:
        # Retrieve the device schema from file
        device_schema = device_exists(DEVICE_SCHEMA_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]  # Extract actual schema fields

        # Define window seconds for streaming aggregation
        window_seconds = 5  # Set the time window in seconds for streaming (adjust as needed)

        # Create the Kafka topic from device_id and run_id
        kafka_topic = f"{device_id}_{run_id}"

        # Start the streaming aggregation with the triggers
        start_streaming_aggregation(kafka_topic, schema_fields, window_seconds, triggers)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start streaming aggregation: {str(e)}")
    

# FastAPI endpoint for stats
@router.get(GET_STATS_ENDPOINT)
async def get_stats(device_id: str, run_id: str, agg_type: str = Query("average", enum=["average", "max", "min", "sum"])):
    """
    Endpoint to fetch aggregated stats for a device and run.
    - device_id: ID of the device
    - run_id: ID of the run
    - agg_type: Type of aggregation (average, max, min, sum). Defaults to "average".
    """
    return await get_aggregated_stats(device_id, run_id, agg_type)


# Endpoint to get the latest stats from the streaming view
@router.get(GET_LATEST_STATS_ENDPOINT)
async def get_latest_stats_endpoint(
    device_id: str,
    run_id: str,
    triggers: Dict[str, List[float]] = Body(..., description="Dictionary with column names and min/max values", embed=True),
    window_seconds: int = Body(5, embed=True)
):
    """
    Endpoint to fetch the latest stats from the streaming view for a device and run.
    - device_id: ID of the device.
    - run_id: ID of the run.
    - triggers: Dictionary with column names and min/max values.
    """
    try:
        kafka_topic = f"{device_id}_{run_id}"
        # Initialize streaming if not already running
        initialize_streaming(device_id, run_id, triggers, window_seconds)

        # Fetch the latest stats from the streaming view
        stats = get_latest_stats(kafka_topic)
        return {"device_id": f'{device_id}_{run_id}', "stats": [row.asDict() for row in stats]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest stats: {str(e)}")