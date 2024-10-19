from typing import Dict, List, Optional, Union
from pyspark.sql import SparkSession

from fastapi import APIRouter, HTTPException, Query, Body
from utils.spark_processor import (
    get_latest_stats,
    check_if_session_exists,
    get_aggregated_stats,initialize_streaming
)
from utils.file_management import kafka_topic_name

router = APIRouter()

GET_STATS_ENDPOINT: str = "/get-stats/{device_id}/{run_id}"
GET_LATEST_STATS_ENDPOINT: str = "/get-latest-stats/{device_id}/{run_id}"
START_STREAM_ENDPOINT: str = "/start-stream/{device_id}/{run_id}"
DEVICE_SCHEMA_PATH: str = "data/device_schemas"


@router.post("/start-stream/{device_id}/{run_id}")
async def start_stream(
    device_id: str,
    run_id: str,
    triggers: Dict[str, List[float]] = Body(..., description="Dictionary with column names and min/max values", embed=True),
    window_seconds: int = Body(5, embed=True),
    table_preappend: Optional[str] = Body(None, embed=True)
) -> Dict[str, str]:
    """
    Endpoint to start the streaming job for a device and run.

    Args:
        device_id (str): ID of the device.
        run_id (str): ID of the run.
        triggers (Dict[str, List[float]]): Dictionary with column names and min/max values.
        window_seconds (int): The window duration in seconds.
        table_preappend (Optional[str]): String to prepend to the table name for the streaming view.

    Returns:
        Dict[str, str]: A message indicating whether the streaming was started or is already running.
    """
    try:
        spark = SparkSession.getActiveSession()
        if spark is not None:
            kafka_topic = kafka_topic_name(device_id, run_id)
            view_name = f"{table_preappend}_{kafka_topic}" if table_preappend else kafka_topic

            if spark.catalog.tableExists(view_name):
                return {"message": f"Streaming already running for device {device_id} and run {run_id}."}

        initialize_streaming(device_id, run_id, triggers, window_seconds, table_preappend)
        return {"message": f"Streaming started for device {device_id} and run {run_id}."}

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start streaming: {str(e)}")


@router.get("/get-latest-stats/{device_id}/{run_id}")
async def get_latest_stats_endpoint(
    device_id: str,
    run_id: str,
    query: str = Query(default="SELECT * FROM {table}", description="SQL query to filter or select data from the streaming view"),
    table_preappend: Optional[str] = Query(None)
) -> Dict[str, Union[str, List[Dict]]]:
    """
    Endpoint to fetch the latest stats from the streaming view for a device and run.

    Args:
        device_id (str): ID of the device.
        run_id (str): ID of the run.
        query (str): SQL query to filter or select data from the streaming view.
        table_preappend (Optional[str]): Optional prefix for the streaming view table name.

    Returns:
        Dict[str, Union[str, List[Dict]]]: A dictionary containing device_id and the retrieved stats as a list of dictionaries.
    """
    try:
        kafka_topic = kafka_topic_name(device_id, run_id)
        view_name = f"{table_preappend}_{kafka_topic}" if table_preappend else kafka_topic

        spark = check_if_session_exists()
        if spark is None or not spark.catalog.tableExists(view_name):
            raise HTTPException(status_code=400, detail=f"Streaming not running for device {device_id} and run {run_id}. Please start the stream first.")

        stats = get_latest_stats(view_name, query)
        return {"device_id": f'{device_id}_{run_id}', "stats": [row.asDict() for row in stats]}

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest stats: {str(e)}")


@router.get(GET_STATS_ENDPOINT)
async def get_stats(
    device_id: str,
    run_id: str,
    agg_type: str = Query("average", enum=["average", "max", "min", "sum"])
) -> Dict[str, Union[str, List[Dict]]]:
    """
    Endpoint to fetch aggregated stats for a device and run.

    Args:
        device_id (str): ID of the device.
        run_id (str): ID of the run.
        agg_type (str): Type of aggregation (average, max, min, sum). Defaults to "average".

    Returns:
        Dict[str, Union[str, List[Dict]]]: A dictionary containing the device_id and the aggregated stats.
    """
    try:
        return await get_aggregated_stats(device_id, run_id, agg_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get aggregated stats: {str(e)}")
