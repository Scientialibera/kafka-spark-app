from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import from_json, col
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
        # Create Spark session
        spark = get_spark_session()

        # Convert the dictionary schema_fields into a PySpark StructType
        struct_schema = convert_schema_to_structtype(schema_fields)

        # Read data from Kafka topic in batch mode
        kafka_df = spark.read \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", device_id) \
            .option("startingOffsets", "earliest") \
            .load()

        # Convert the binary 'value' column from Kafka to a string
        value_df = kafka_df.selectExpr("CAST(value AS STRING) as json_string", "timestamp")

        # Parse the JSON string into a DataFrame using the StructType schema
        json_df = value_df.select(
            from_json(col("json_string"), struct_schema).alias("data"),
            "timestamp"
        )

        # Flatten the nested 'data' column to access individual fields
        data_df = json_df.select("data.*")

        # Dynamically generate aggregation expressions based on aggregation type
        aggregations = generate_aggregations(schema_fields, agg_type)

        # Perform aggregation
        aggregated_df = data_df.agg(*aggregations)

        # Collect the result as a dictionary
        result = aggregated_df.collect()[0].asDict()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Kafka batch: {str(e)}")