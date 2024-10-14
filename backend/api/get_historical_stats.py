from fastapi import APIRouter, HTTPException

router = APIRouter()

GET_HISTORICAL_AVERAGE_ENDPOINT = "/get-average/{device_id}/{run_id}"
GET_HISTORICA_MAX_ENDPOINT = "/get-max/{device_id}/{run_id}"

# Generic endpoint function for getting aggregated stats
@router.get(GET_HISTORICAL_AVERAGE_ENDPOINT)
async def get_historical_average_stats(device_id: str, run_id: str):
    return {"message": "Get historical average stats."}
