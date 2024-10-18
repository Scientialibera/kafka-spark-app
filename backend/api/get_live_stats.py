from typing import Dict, List
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException, Query, Body
from utils.spark_processor import get_kafka_batch_aggregates, get_kafka_batch_with_threshold_check
from utils.file_management import device_exists

router = APIRouter()

GET_STATS_ENDPOINT = "/get-stats/{device_id}/{run_id}"
GET_THRESHOLD_STATS_ENDPOINT = "/get-threshold-stats/{device_id}/{run_id}"
DEVICE_SCHEMA_PATH = "data/device_schemas"

# Create a ThreadPoolExecutor for concurrent Spark jobs
executor = ThreadPoolExecutor(max_workers=12)

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
    

# Generic endpoint function for checking threshold stats
async def get_threshold_stats(device_id: str, run_id: str, rate: float, window_seconds: int, triggers: dict):
    loop = asyncio.get_event_loop()
    try:
        # Retrieve the device schema from file
        device_schema = device_exists(DEVICE_SCHEMA_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]  # Extract actual schema fields

        # Get the Kafka stream and apply threshold checks (run in a thread to avoid blocking)
        kafka_topic = f"{device_id}_{run_id}"
        result = await loop.run_in_executor(executor, get_kafka_batch_with_threshold_check, kafka_topic, schema_fields, rate, window_seconds, triggers)

        # Format the response
        response = {"device_id": device_id, "run_id": run_id, "status": result}

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch threshold stats: {str(e)}")
    

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


# FastAPI endpoint for threshold stats
@router.post(GET_THRESHOLD_STATS_ENDPOINT)
async def get_threshold_stats_endpoint(
    device_id: str,
    run_id: str,
    rate: float = Body(..., embed=True),
    window_seconds: int = Body(..., embed=True),
    triggers: Dict[str, List[float]] = Body(..., description="Dictionary with column names and min/max values", embed=True)
):
    """
    Endpoint to fetch stats and evaluate against threshold triggers for a device and run.
    - device_id: ID of the device
    - run_id: ID of the run
    - rate: Kafka update rate (in seconds).
    - window_seconds: Time window to analyze (in seconds).
    - triggers: Dictionary with column names and min/max values.
    """
    return await get_threshold_stats(device_id, run_id, rate, window_seconds, triggers)