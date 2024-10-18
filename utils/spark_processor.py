from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import from_json, col, expr, window
from fastapi import HTTPException
from pyspark.sql.types import StructType, StructField, StringType, FloatType, IntegerType

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


def get_spark_session():
    """Create or get an existing Spark session."""
    spark = SparkSession.getActiveSession()  # Check if a session exists
    if not spark:  # If no session exists, create a new one
        spark = SparkSession.builder \
            .appName("Kafka Streaming Stats") \
            .master("local[*]") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
            .config("spark.sql.warehouse.dir", "/tmp") \
            .config("spark.hadoop.fs.defaultFS", "file:///") \
            .config("spark.hadoop.io.nativeio.disable", "true") \
            .getOrCreate()
    return spark


def read_kafka_data(device_id: str, schema_fields: dict, time_window_seconds: int = None):
    """
    Read and process Kafka data based on the device ID and schema.
    If time_window_seconds is provided, it filters the data to only include the last messages within that time window.
    """
    try:
        # Create Spark session
        spark = get_spark_session()

        # Convert the dictionary schema_fields into a PySpark StructType
        struct_schema = convert_schema_to_structtype(schema_fields)

        # Read data from Kafka topic in batch mode using the "earliest" offset
        kafka_df = spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", device_id) \
            .option("startingOffsets", "earliest") \
            .load()

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

def start_streaming_aggregation(kafka_topic: str, schema_fields: dict, window_seconds: int, triggers: dict):
    """
    Set up a streaming threshold check on the Kafka stream for the given Kafka topic.
    If the query is already running, it will return the existing query.
    """
    # Create Spark session
    spark = SparkSession.builder \
        .appName("Kafka Streaming Stats") \
        .master("local[*]") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3") \
        .getOrCreate()

    # Check if a streaming query with this Kafka topic is already running
    query_name = f"device_threshold_view_{kafka_topic}"
    active_queries = [q for q in spark.streams.active if q.name == query_name]

    if active_queries:
        print(f"Streaming query for topic {kafka_topic} is already running.")
        return active_queries[0]

    # Convert the dictionary schema_fields into a PySpark StructType
    struct_schema = StructType([
        StructField(field, FloatType() if ftype == "float" else StringType() if ftype == "string" else IntegerType(), True)
        for field, ftype in schema_fields.items()
    ])

    # Read the streaming data from Kafka
    kafka_stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", "latest") \
        .load()

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

    # Apply the threshold checks based on triggers
    for field, (min_val, max_val) in triggers.items():
        if field in schema_fields and schema_fields[field] in ["float", "int"]:
            # Create conditions for checking threshold violations
            data_df = data_df.withColumn(f"{field}_status",
                                         F.when(col(field) < min_val, "low")
                                         .when(col(field) > max_val, "high")
                                         .otherwise("normal"))

    # Write the result with status checks to an in-memory table with a unique query name for this device
    query = data_df.writeStream \
        .outputMode("append") \
        .format("memory") \
        .queryName(query_name) \
        .trigger(processingTime=f"{window_seconds} seconds") \
        .start()

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


def get_latest_stats(device_id: str):
    """
    Retrieve the latest stats from the in-memory table for the given device ID.
    """
    spark = SparkSession.getActiveSession()
    if spark is None:
        raise Exception("No active Spark session found")

    # Construct the view name based on the device_id
    view_name = f"device_threshold_view_{device_id}"

    # Check if the view exists before querying
    if not spark.catalog.tableExists(view_name):
        raise Exception(f"The table or view {view_name} cannot be found.")

    # Query the in-memory table for the latest result
    stats_df = spark.sql(f"SELECT * FROM {view_name}")
    return stats_df.collect()