import os
from typing import Dict, Union

from fastapi import APIRouter, HTTPException

from backend.config.config import HISTORICAL_DATA_PATH

router = APIRouter()

GET_HISTORICAL_AVERAGE_ENDPOINT: str = "/get-average/{device_id}/{run_id}"
GET_HISTORICAL_MAX_ENDPOINT: str = "/get-max/{device_id}/{run_id}"
DELETE_HISTORICAL_DATA_ENDPOINT: str = "/delete/{device_id}/{run_id}"
DELETE_ALL_HISTORICAL_DATA_ENDPOINT: str = "/delete-all"

# Generic endpoint function for getting aggregated historical stats
@router.get(GET_HISTORICAL_AVERAGE_ENDPOINT)
async def get_historical_average_stats(device_id: str, run_id: str):
    return {"message": "Get historical average stats."}


import shutil  # Import shutil for directory removal

@router.delete(DELETE_ALL_HISTORICAL_DATA_ENDPOINT)
async def delete_all_historical_data() -> Dict[str, Union[str, int]]:
    """
    Endpoint to delete all historical data files and folders in the specified directory.

    Returns:
        Dict[str, Union[str, int]]: A message indicating the result of the deletion and the count of items deleted.
    """
    try:
        # Check if the path exists
        if not os.path.exists(HISTORICAL_DATA_PATH):
            raise HTTPException(status_code=404, detail="Historical data path does not exist.")

        # List all items in the directory
        items = os.listdir(HISTORICAL_DATA_PATH)
        deleted_count = 0

        # Delete each item in the directory
        for item_name in items:
            item_path = os.path.join(HISTORICAL_DATA_PATH, item_name)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Recursively delete directories
            deleted_count += 1

        return {"message": "All historical data files and folders deleted successfully", "deleted_items_count": deleted_count}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete all historical data: {str(e)}")


