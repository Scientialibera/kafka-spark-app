"""
Spark processing utilities for Kafka stream analysis.

This module provides functions for reading Kafka data with Spark,
performing aggregations, and managing streaming queries.
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, from_json
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import FloatType, IntegerType, StringType, StructField, StructType

from backend.config.config import (
    KAFKA_BROKER_URL,
    MAX_WORKERS,
    SCHEMA_DATA_PATH,
    SPARK_APP_NAME,
    SPARK_MASTER_URL,
)
from utils.file_management import device_exists, kafka_topic_name

logger = logging.getLogger(__name__)

# Path to device schemas
DEVICE_SCHEMA_PATH = SCHEMA_DATA_PATH

# Thread pool for concurrent Spark jobs
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

# Dictionary to track active streaming queries
streaming_queries: Dict[str, StreamingQuery] = {}


def check_if_session_exists() -> Optional[SparkSession]:
    """
    Check if an active Spark session exists.
    
    Returns:
        Active SparkSession or None
    """
    return SparkSession.getActiveSession()


def convert_schema_to_structtype(schema_fields: Dict[str, str]) -> StructType:
    """
    Convert a schema dictionary into a PySpark StructType.
    
    Args:
        schema_fields: Dictionary mapping field names to type strings
        
    Returns:
        PySpark StructType schema
        
    Raises:
        ValueError: If an unsupported data type is encountered
    """
    type_mapping = {
        "float": FloatType(),
        "int": IntegerType(),
        "string": StringType(),
    }
    
    struct_fields = []
    for field_name, field_type in schema_fields.items():
        spark_type = type_mapping.get(field_type)
        if spark_type is None:
            raise ValueError(f"Unsupported data type: {field_type}")
        struct_fields.append(StructField(field_name, spark_type, True))
    
    return StructType(struct_fields)


def get_spark_session(
    app_name: str = SPARK_APP_NAME,
    master_url: str = SPARK_MASTER_URL
) -> SparkSession:
    """
    Get or create a Spark session.
    
    Args:
        app_name: Name for the Spark application
        master_url: Spark master URL
        
    Returns:
        SparkSession instance
        
    Raises:
        Exception: If session creation fails
    """
    try:
        spark = (
            SparkSession.builder
            .appName(app_name)
            .master(master_url)
            .config(
                "spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3"
            )
            .getOrCreate()
        )
        logger.info("Spark session created successfully")
        return spark
    except Exception as e:
        logger.error(f"Failed to create Spark session: {e}")
        raise


def read_kafka_stream(
    spark: SparkSession,
    kafka_topic: str,
    offset: str = "latest"
) -> DataFrame:
    """
    Read a streaming DataFrame from Kafka.
    
    Args:
        spark: SparkSession instance
        kafka_topic: Kafka topic to subscribe to
        offset: Starting offset ('latest' or 'earliest')
        
    Returns:
        Streaming DataFrame
    """
    return (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER_URL)
        .option("subscribe", kafka_topic)
        .option("startingOffsets", offset)
        .load()
    )


def read_kafka_batch(
    spark: SparkSession,
    kafka_topic: str,
    offset: str = "earliest"
) -> DataFrame:
    """
    Read a batch DataFrame from Kafka.
    
    Args:
        spark: SparkSession instance
        kafka_topic: Kafka topic to read from
        offset: Starting offset ('latest' or 'earliest')
        
    Returns:
        Batch DataFrame
    """
    return (
        spark.read
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER_URL)
        .option("subscribe", kafka_topic)
        .option("startingOffsets", offset)
        .load()
    )


def write_stream_to_memory(
    stream_df: DataFrame,
    table_name: str,
    trigger_time: int = 5
) -> StreamingQuery:
    """
    Write a streaming DataFrame to an in-memory table.
    
    Args:
        stream_df: Streaming DataFrame to write
        table_name: Name for the in-memory table
        trigger_time: Processing trigger interval in seconds
        
    Returns:
        StreamingQuery handle
    """
    return (
        stream_df.writeStream
        .outputMode("append")
        .format("memory")
        .queryName(table_name)
        .trigger(processingTime=f'{trigger_time} seconds')
        .start()
    )


def read_kafka_data(
    device_id: str,
    schema_fields: Dict[str, str],
    time_window_seconds: Optional[int] = None
) -> DataFrame:
    """
    Read and process Kafka data for a device.
    
    Args:
        device_id: Device identifier (used as Kafka topic)
        schema_fields: Schema definition for parsing messages
        time_window_seconds: Optional time window filter in seconds
        
    Returns:
        Processed DataFrame with parsed data
        
    Raises:
        HTTPException: If an error occurs reading the data
    """
    try:
        spark = get_spark_session()
        
        logger.debug(f"Reading Kafka data for device: {device_id}")
        logger.debug(f"Spark Master: {spark.sparkContext.master}")
        
        # Convert schema to StructType
        struct_schema = convert_schema_to_structtype(schema_fields)

        # Read data from Kafka topic in batch mode
        kafka_df = read_kafka_batch(spark, device_id)

        # Convert binary value to string
        value_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string")

        # Parse the JSON string into a DataFrame using the StructType schema
        json_df = value_df.select(
            from_json(col("json_string"), struct_schema).alias("data")
        )

        # Flatten the nested 'data' column to access individual fields
        data_df = json_df.select("data.*")

        # Ensure the timestamp column is cast properly as a timestamp type
        data_df = data_df.withColumn("timestamp", col("timestamp").cast("timestamp"))

        # If a time window is provided, filter the data based on the timestamp
        if time_window_seconds is not None:
            # Get the current maximum timestamp
            max_timestamp = data_df.agg(F.max("timestamp")).collect()[0][0]

            # Filter the data to only include records within the specified time window
            filtered_data_df = data_df.filter(
                col("timestamp") >= F.expr(f"timestamp'{max_timestamp}' - interval {time_window_seconds} seconds")
            )

            return filtered_data_df

        # If no time window is specified, return the entire DataFrame
        return data_df

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading Kafka data: {str(e)}")


# Dictionary to keep track of active streaming queries by device_id
streaming_queries = {}

def start_streaming_aggregation(kafka_topic: str, schema_fields: dict, window_seconds: int, triggers: dict, table_preappend: str = None, kafka_streaming_app: str = SPARK_APP_NAME, exclude_normal: bool = False):
    """
    Set up streaming threshold monitoring on a Kafka topic.
    
    Creates a streaming query that checks values against thresholds
    and writes alerts to an in-memory table.
    
    Args:
        kafka_topic: Kafka topic to monitor
        schema_fields: Schema definition for the topic
        window_seconds: Processing window in seconds
        triggers: Dictionary mapping fields to (min, max) thresholds
        table_preappend: Optional prefix for the table name
        kafka_streaming_app: Spark application name
        exclude_normal: Whether to exclude normal values
        
    Returns:
        StreamingQuery handle
    """
    spark = get_spark_session(kafka_streaming_app)
    
    table_name = f"{table_preappend}_{kafka_topic}" if table_preappend else kafka_topic

    # Check for existing query
    active_queries = [q for q in spark.streams.active if q.name == table_name]
    if active_queries:
        logger.info(f"Streaming query for topic {kafka_topic} is already running")
        return active_queries[0]

    # Convert schema to StructType
    struct_schema = convert_schema_to_structtype(schema_fields)

    # Read streaming data from Kafka
    kafka_stream = read_kafka_stream(spark, kafka_topic)

    # Parse JSON messages
    value_df = kafka_stream.selectExpr("CAST(value AS STRING) as json_string")
    json_df = value_df.select(
        from_json(col("json_string"), struct_schema).alias("data")
    )
    data_df = json_df.select("data.*")

    # Cast timestamp column
    data_df = data_df.withColumn("timestamp", col("timestamp").cast("timestamp"))

    # Add status columns for threshold checking
    status_columns = []
    for field, (min_val, max_val) in triggers.items():
        if field in schema_fields and schema_fields[field] in ["float", "int"]:
            logger.debug(f"Adding threshold check for {field}: [{min_val}, {max_val}]")
            
            status_column = (
                F.when(F.col(field) < F.lit(min_val), "low")
                .when(F.col(field) > F.lit(max_val), "high")
                .otherwise("normal")
            )
            
            status_column_name = f"{field}_status"
            data_df = data_df.withColumn(status_column_name, status_column)
            status_columns.append(status_column_name)

    # Build filter condition for non-normal values
    combined_condition = F.lit(False)
    for col_name in status_columns:
        combined_condition = combined_condition | (F.col(col_name) != "normal")

    # Apply filter to exclude normal values
    data_df = data_df.filter(combined_condition).coalesce(1)

    # Write to in-memory table
    query = write_stream_to_memory(data_df, table_name, window_seconds)

    # Track the query
    streaming_queries[kafka_topic] = query

    logger.info(f"Streaming initialized for topic: {kafka_topic}")

    return query


def get_aggregation_function(agg_type: str):
    """Return the appropriate aggregation function based on the aggregation type."""
    if agg_type == 'average':
        return F.avg
    elif agg_type == 'max':
        return F.max
    else:
        raise ValueError(f"Unsupported aggregation type: {agg_type}")


def generate_aggregations(schema_fields, agg_type):
    """
    Generate dynamic aggregation expressions based on schema and aggregation type.
    """
    agg_func = get_aggregation_function(agg_type)
    
    aggregations = []
    for field, field_type in schema_fields.items():
        if field_type == "float" or field_type == "int":  # Aggregate only numeric fields
            aggregations.append(agg_func(F.col(field)).alias(f"{agg_type}_{field}"))
    return aggregations


# Function to process Kafka stream and calculate dynamic aggregates
def get_kafka_batch_aggregates(device_id: str, schema_fields: dict, agg_type: str):
    """
    Process the Kafka batch data for the given device ID and schema fields.
    """
    try:
        # Read the processed Kafka DataFrame using the new utility function (no time window for aggregation)
        data_df = read_kafka_data(device_id, schema_fields)

        # Dynamically generate aggregation expressions based on aggregation type
        aggregations = generate_aggregations(schema_fields, agg_type)

        # Perform aggregation
        aggregated_df = data_df.agg(*aggregations)

        # Collect the result as a dictionary
        result = aggregated_df.collect()[0].asDict()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Kafka batch: {str(e)}")


def get_latest_stats(table: str, query: str):
    """
    Retrieve the latest stats from the in-memory table for the given device ID based on the provided query.
    """
    spark = check_if_session_exists()
    if spark is None:
        raise Exception("No active Spark session found")

    # Check if the view exists before querying
    if not spark.catalog.tableExists(table):
        raise Exception(f"The table or view {table} cannot be found.")

    # Format the query to safely include the view name
    try:
        formatted_query = query.format(table=table)
    except KeyError:
        raise Exception("The query string must include '{table}' placeholder for the view name.")

    # Execute the SQL query
    try:
        stats_df = spark.sql(formatted_query)
        return stats_df.collect()
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")

# Generic endpoint function for getting aggregated stats
async def get_aggregated_stats(device_id: str, run_id: str, agg_type: str):
    loop = asyncio.get_event_loop()
    try:
        # Retrieve the device schema from file
        device_schema = device_exists(DEVICE_SCHEMA_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]  # Extract actual schema fields

        # Get the Kafka stream and apply dynamic aggregation (run in a thread to avoid blocking)
        kafka_topic = kafka_topic_name(device_id, run_id)
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
def initialize_streaming(device_id: str, run_id: str, triggers: dict, window_seconds: int = 5, table_preappend: str = None, exclude_normal: bool = False):
    """
    Initialize the streaming aggregation for the given device and run ID if it's not already running.
    """
    try:
        # Retrieve the device schema from file
        device_schema = device_exists(DEVICE_SCHEMA_PATH, device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]  # Extract actual schema fields

        # Create the Kafka topic from device_id and run_id
        kafka_topic = kafka_topic_name(device_id, run_id)

        # Start the streaming aggregation with the triggers and optional table_preappend
        start_streaming_aggregation(kafka_topic, schema_fields, window_seconds, triggers, table_preappend, exclude_normal)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start streaming aggregation: {str(e)}")
    