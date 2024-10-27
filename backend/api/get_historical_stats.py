import os
from typing import Dict, Union

from fastapi import APIRouter, HTTPException

from backend.config.config import HISTORICAL_DATA_PATH

router = APIRouter()

GET_HISTORICAL_AVERAGE_ENDPOINT = "/get-average/{device_id}/{run_id}"
GET_HISTORICAL_MAX_ENDPOINT = "/get-max/{device_id}/{run_id}"
DELETE_HISTORICAL_DATA_ENDPOINT = "/delete/{device_id}/{run_id}"
DELETE_ALL_HISTORICAL_DATA_ENDPOINT = "/delete-all"

# Generic endpoint function for getting aggregated historical stats
@router.get(GET_HISTORICAL_AVERAGE_ENDPOINT)
async def get_historical_average_stats(device_id: str, run_id: str):
    return {"message": "Get historical average stats."}


@router.delete(DELETE_ALL_HISTORICAL_DATA_ENDPOINT)
async def delete_all_historical_data() -> Dict[str, Union[str, int]]:
    """
    Endpoint to delete all historical data files in the specified directory.

    Returns:
        Dict[str, Union[str, int]]: A message indicating the result of the deletion and the count of files deleted.
    """
    try:
        # Check if the path exists
        if not os.path.exists(HISTORICAL_DATA_PATH):
            raise HTTPException(status_code=404, detail="Historical data path does not exist.")

        # List all files in the directory
        files = os.listdir(HISTORICAL_DATA_PATH)
        deleted_count = 0

        # Delete each file
        for file_name in files:
            file_path = os.path.join(HISTORICAL_DATA_PATH, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                deleted_count += 1

        return {"message": "All historical data files deleted successfully", "deleted_files_count": deleted_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete all historical data: {str(e)}")


