from fastapi import APIRouter, HTTPException
from utils.spark_processor import get_kafka_batch_aggregates
from utils.file_management import device_exists

router = APIRouter()

GET_AVERAGE_ENDPOINT = "/get-average/{device_id}/{run_id}"
GET_MAX_ENDPOINT = "/get-max/{device_id}/{run_id}"

# Generic endpoint function for getting aggregated stats
def get_aggregated_stats(device_id: str, run_id: str, agg_type: str):
    try:
        # Retrieve the device schema from file
        device_schema = device_exists("data/device_schemas", device_id, raise_error_if_not_found=True)
        schema_fields = device_schema["schema"]  # Extract actual schema fields

        # Get the Kafka stream and apply dynamic aggregation
        kafka_topic = f"{device_id}_{run_id}"
        result = get_kafka_batch_aggregates(kafka_topic, schema_fields, agg_type)

        # Format the result dynamically
        response = {"device_id": device_id}
        for field in schema_fields.keys():
            if schema_fields[field] in ["float", "int"]:  # Include only numeric fields in the response
                response[f"{agg_type}_{field}"] = result.get(f"{agg_type}_{field}", None)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch {agg_type} stats: {str(e)}")
    

# FastAPI endpoints for average and max stats
@router.get(GET_AVERAGE_ENDPOINT)
async def get_average_stats(device_id: str, run_id: str):
    return get_aggregated_stats(device_id, run_id,"average")

@router.get(GET_MAX_ENDPOINT)
async def get_max_stats(device_id: str, run_id: str):
    return get_aggregated_stats(device_id, run_id, "max")
