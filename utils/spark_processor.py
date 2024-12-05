import asyncio
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from fastapi import HTTPException
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructField, StructType,  FloatType, IntegerType, StringType

from utils.file_management import device_exists, kafka_topic_name
from backend.config.config import MAX_WORKERS, SPARK_APP_NAME, SPARK_MASTER_URL, KAFKA_BROKER_URL, SCHEMA_DATA_PATH

DEVICE_SCHEMA_PATH = SCHEMA_DATA_PATH

# Create a ThreadPoolExecutor for concurrent Spark jobs
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def check_if_session_exists():
    """Check if a Spark session exists."""
    spark = SparkSession.getActiveSession()
    if not spark:
        return
    return spark


def convert_schema_to_structtype(schema_fields):
    """
    Convert schema_fields dictionary into a PySpark StructType schema.
    """
    struct_fields = []
    
    for field_name, field_type in schema_fields.items():
        if field_type == "float":
            struct_fields.append(StructField(field_name, FloatType(), True))
        elif field_type == "int":
            struct_fields.append(StructField(field_name, IntegerType(), True))
        elif field_type == "string":
            struct_fields.append(StructField(field_name, StringType(), True))
        else:
            raise ValueError(f"Unsupported data type: {field_type}")

    return StructType(struct_fields)


def get_spark_session(app_name="Kafka Streaming Stats", master_url=SPARK_MASTER_URL):
    try:
        spark = SparkSession.builder \
            .appName(app_name) \
            .master(master_url) \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
            .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
            .config("spark.sql.catalogImplementation", "in-memory") \
            .config("spark.local.dir", "/tmp/spark-temp") \
            .config("spark.driver.host", "0.0.0.0") \
            .config("spark.driver.bindAddress", "0.0.0.0") \
            .config("spark.kafka.bootstrap.servers", KAFKA_BROKER_URL) \
            .getOrCreate()
        print("Spark session created successfully.")
        return spark
    except Exception as e:
        print("Failed to create Spark session:", e)
        raise


def read_kafka_stream(spark, kafka_topic: str, offset: str = "latest"):
    """
    Reads and returns a streaming DataFrame from Kafka for the given topic.
    """
    return spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER_URL) \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", offset) \
        .load()


def read_kafka_batch(spark, kafka_topic: str, offset: str = "earliest"):
    """
    Reads and returns a batch DataFrame from Kafka for the given topic.
    """
    return spark.read \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER_URL) \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", offset) \
        .load()


def write_stream_to_memory(stream_df, table_name, trigger_time=5):
    """
    Write the streaming DataFrame to an in-memory table with the given name.
    """
    return stream_df.writeStream \
        .outputMode("append") \
        .format("memory") \
        .queryName(table_name) \
        .trigger(processingTime=f'{trigger_time} seconds') \
        .start()


def read_kafka_data(device_id: str, schema_fields: dict, time_window_seconds: int = None):
    """
    Read and process Kafka data based on the device ID and schema.
    If time_window_seconds is provided, it filters the data to only include the last messages within that time window.
    """
    try:
        # Create Spark session
        spark = get_spark_session()
        
        # Print Spark session and configuration details
        print("Spark session information:")
        print(f" - App Name: {spark.sparkContext.appName}")
        print(f" - Master URL: {spark.sparkContext.master}")
        print(f" - Spark UI URL: {spark.sparkContext.uiWebUrl}")
        print(f" - Spark Version: {spark.version}")
        
        # Get Spark configuration settings
        print("Spark Configuration:")
        for key, value in spark.sparkContext.getConf().getAll():
            print(f"   {key}: {value}")
        
        # Print worker details
        print("Spark Workers Information:")
        print(f" - Executor memory: {spark.sparkContext.getConf().get('spark.executor.memory')}")
        print(f" - Executor cores: {spark.sparkContext.getConf().get('spark.executor.cores')}")
        
        # Convert the dictionary schema_fields into a PySpark StructType
        struct_schema = convert_schema_to_structtype(schema_fields)

        # Read data from Kafka topic in batch mode using the "earliest" offset
        kafka_df = read_kafka_batch(spark, device_id)

        # Convert the binary 'value' column from Kafka to a string and drop the Kafka timestamp
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
    Set up a streaming threshold check on the Kafka stream for the given Kafka topic.
    If the query is already running, it will return the existing query.
    """
    # Create Spark session
    spark = get_spark_session(kafka_streaming_app)
    
    table_name = f"{table_preappend}_{kafka_topic}" if table_preappend else kafka_topic

    # Check if a streaming query with this Kafka topic is already running
    active_queries = [q for q in spark.streams.active if q.name == table_name]

    if active_queries:
        print(f"Streaming query for topic {kafka_topic} is already running.")
        return active_queries[0]

    # Convert the dictionary schema_fields into a PySpark StructType
    struct_schema = StructType([
        StructField(field, FloatType() if ftype == "float" else StringType() if ftype == "string" else IntegerType(), True)
        for field, ftype in schema_fields.items()
    ])

    # Read the streaming data from Kafka
    kafka_stream = read_kafka_stream(spark, kafka_topic)

    # Convert the binary 'value' column from Kafka to a string and drop the Kafka timestamp
    value_df = kafka_stream.selectExpr("CAST(value AS STRING) as json_string")

    # Parse the JSON string into a DataFrame using the StructType schema
    json_df = value_df.select(
        from_json(col("json_string"), struct_schema).alias("data")
    )

    # Flatten the nested 'data' column to access individual fields, including the timestamp from the JSON data
    data_df = json_df.select("data.*")

    # Ensure the timestamp column from the JSON is cast as a timestamp type
    data_df = data_df.withColumn("timestamp", col("timestamp").cast("timestamp"))

    status_columns = []
    for field, (min_val, max_val) in triggers.items():
        if field in schema_fields and schema_fields[field] in ["float", "int"]:
            print(f"Adding status check for field: {field} with min: {min_val} and max: {max_val}.")
            
            status_column = F.when(F.col(field) < F.lit(min_val), "low") \
                             .when(F.col(field) > F.lit(max_val), "high") \
                             .otherwise("normal")
            
            status_column_name = f"{field}_status"
            data_df = data_df.withColumn(status_column_name, status_column)
            status_columns.append(status_column_name)

    combined_condition = F.lit(False)
    for col_name in status_columns:
        combined_condition = combined_condition | (F.col(col_name) != "normal")

    # Apply the filter to exclude rows where all status columns are 'normal'
    data_df = data_df.filter(combined_condition).coalesce(1)

    # Write the result with status checks to an in-memory table with a unique query name for this device
    query = write_stream_to_memory(data_df, table_name, window_seconds)

    # Store the reference to the query so we can manage it later
    streaming_queries[kafka_topic] = query

    print(f"Streaming initialized for topic: {kafka_topic}")

    return query


def get_aggregation_function(agg_type):
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
    