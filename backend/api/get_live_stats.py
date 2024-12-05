from typing import Dict, List, Optional, Union

from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from fastapi import APIRouter, HTTPException, Query, Body
import asyncio

from utils.spark_processor import (
    get_latest_stats,
    check_if_session_exists,
    get_aggregated_stats,
    initialize_streaming
)
from utils.file_management import kafka_topic_name
from utils.maths_functions import calculate_speed_from_messages, calculate_acceleration_from_messages
from .kafka_topics import get_topic_messages
from backend.config.config import SCHEMA_DATA_PATH

router = APIRouter()

GET_STATS_ENDPOINT: str = "/get-stats/{device_id}/{run_id}"
GET_INSTANT_SPEED_ACCEL_ENDPOINT: str = "/get-speed/{device_id}/{run_id}"
START_STREAM_ENDPOINT: str = "/start-stream/{device_id}/{run_id}"
ALARM_ENDPOINT: str = "/get-notification/{device_id}/{run_id}"

DEVICE_SCHEMA_PATH: str = SCHEMA_DATA_PATH


@router.post(START_STREAM_ENDPOINT)
async def start_stream(
    device_id: str,
    run_id: str,
    triggers: Dict[str, List[float]] = Body(..., description="Dictionary with column names and min/max values", embed=True),
    window_seconds: int = Body(5, embed=True),
    table_preappend: Optional[str] = Body(None, embed=True),
    exclude_normal: Optional[bool] = Body(False, embed=True)

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
        spark = check_if_session_exists()
        if spark is not None:
            kafka_topic = kafka_topic_name(device_id, run_id)
            view_name = f"{table_preappend}_{kafka_topic}" if table_preappend else kafka_topic

            if spark.catalog.tableExists(view_name):
                return {"message": f"Streaming already running for device {device_id} and run {run_id}."}
            else:
                initialize_streaming(device_id, run_id, triggers, window_seconds, table_preappend, exclude_normal)

        initialize_streaming(device_id, run_id, triggers, window_seconds, table_preappend, exclude_normal)
        return {"message": f"Streaming started for device {device_id} and run {run_id}."}

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start streaming: {str(e)}")


# @router.get(QUERY_VIEW)
# async def QUERY_VIEW(
#     device_id: str,
#     run_id: str,
#     query: str = Query(default="SELECT * FROM {table}", description="SQL query to filter or select data from the streaming view"),
#     table_preappend: Optional[str] = Query(None)
# ) -> Dict[str, Union[str, List[Dict]]]:
#     """
#     Endpoint to fetch the latest stats from the streaming view for a device and run.

#     Args:
#         device_id (str): ID of the device.
#         run_id (str): ID of the run.
#         query (str): SQL query to filter or select data from the streaming view.
#         table_preappend (Optional[str]): Optional prefix for the streaming view table name.

#     Returns:
#         Dict[str, Union[str, List[Dict]]]: A dictionary containing device_id and the retrieved stats as a list of dictionaries.
#     """
#     try:
#         kafka_topic = kafka_topic_name(device_id, run_id)
#         view_name = f"{table_preappend}_{kafka_topic}" if table_preappend else kafka_topic

#         spark = check_if_session_exists()
#         if spark is None or not spark.catalog.tableExists(view_name):
#             raise HTTPException(status_code=400, detail=f"Streaming not running for device {device_id} and run {run_id}. Please start the stream first.")

#         stats = get_latest_stats(view_name, query)
#         return {"device_id": f'{device_id}_{run_id}', "stats": [row.asDict() for row in stats]}

#     except HTTPException as http_ex:
#         raise http_ex
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to fetch latest stats: {str(e)}")


@router.get(GET_STATS_ENDPOINT)
async def get_stats(
    device_id: str,
    run_id: str,
    agg_type: str = Query("average", enum=["average", "max", "min", "sum"])
) -> Dict:
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


@router.get(GET_INSTANT_SPEED_ACCEL_ENDPOINT)
async def get_metric(
    device_id: str,
    run_id: str,
    type: str  # "speed" or "acceleration"
) -> Dict[str, Union[str, float]]:
    """
    Endpoint to fetch either instantaneous speed or acceleration for a device and run.

    Args:
        device_id (str): ID of the device.
        run_id (str): ID of the run.
        type (str): Type of metric to calculate ("speed" or "acceleration").

    Returns:
        Dict[str, Union[str, float]]: A dictionary containing the device_id, run_id, and the calculated metric.
    """
    try:
        # Fetch the latest 3 messages from Kafka for acceleration or 2 for speed
        limit = 3 if type == "acceleration" else 2
        response = await get_topic_messages(device_id, run_id, limit=limit)

        # Extract the messages from the response
        messages = response.get("messages", [])

        # Validate data availability
        if (type == "speed" and len(messages) < 2) or (type == "acceleration" and len(messages) < 3):
            raise HTTPException(status_code=400, detail=f"Not enough data to calculate {type}. Please ensure there are active sensors producing data.")

        # Sort messages by timestamp to ensure they are in chronological order
        sorted_messages = sorted(messages, key=lambda msg: msg["timestamp"])

        # Calculate the requested metric
        if type == "speed":
            metric = calculate_speed_from_messages(sorted_messages)
        elif type == "acceleration":
            metric = calculate_acceleration_from_messages(sorted_messages)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid type '{type}'. Must be 'speed' or 'acceleration'.")

        return {
            "device_id": device_id,
            "run_id": run_id,
            type: metric
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get {type}: {str(e)}")
    

@router.get(ALARM_ENDPOINT)
async def get_notification(device_id: str, run_id: str, window: int = 1, table_preappend: Union[str, None] = None) -> StreamingResponse:
    """
    Endpoint to provide live notifications while the stream is active for a device and run.

    Args:
        device_id (str): ID of the device.
        run_id (str): ID of the run.
        window (int): Interval in seconds between data fetch attempts.
        table_preappend (Optional[str]): Optional prefix for the streaming view table name.

    Returns:
        StreamingResponse: A live streaming response with data updates.
    """
    kafka_topic = kafka_topic_name(device_id, run_id)
    view_name = f"{table_preappend}_{kafka_topic}" if table_preappend else kafka_topic

    async def event_generator():
        try:
            spark = check_if_session_exists()
            if spark is None:
                raise HTTPException(status_code=400, detail="Spark session not available")

            # Variable to keep track of the last processed timestamp
            last_processed_timestamp = None

            while True:
                # Check if the view exists
                if not spark.catalog.tableExists(view_name):
                    # If the view is gone, close the connection
                    break

                # Fetch the latest data from the view
                try:
                    # Query the view and order by timestamp descending to get the latest row
                    query = f"SELECT * FROM {view_name} ORDER BY timestamp DESC LIMIT 1"
                    data_df = spark.sql(query)

                    # Convert the DataFrame to a dictionary
                    data = [row.asDict() for row in data_df.collect()]

                    if data:
                        latest_row = data[0]
                        current_timestamp = latest_row.get("timestamp")

                        # Only yield if the current timestamp is newer than the last processed timestamp
                        if last_processed_timestamp is None or current_timestamp > last_processed_timestamp:
                            # Update the last processed timestamp
                            last_processed_timestamp = current_timestamp
                            # Yield the latest data as an SSE message
                            yield {
                                "event": "update",
                                "data": {"device_id": f"{device_id}_{run_id}", "updates": [latest_row]}
                            }

                except Exception as e:
                    # Log or handle error
                    print(f"Error fetching data from view {view_name}: {str(e)}")

                # Wait for the specified interval before checking again
                await asyncio.sleep(window)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    # Return the event stream response
    return EventSourceResponse(event_generator())
