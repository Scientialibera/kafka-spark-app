import json
import os
from fastapi import APIRouter, HTTPException

from backend.models.schemas import RegisterDeviceRequest
from utils.file_management import create_folder, save_json_file, convert_model_to_json

router = APIRouter()


# Set the path where schemas will be saved
SCHEMA_SAVE_PATH = os.path.join("data", "device_schemas")  # Join with data/device_schemas path


@router.post("/register-device")
async def register_device_schema(device: RegisterDeviceRequest):
    # Ensure the schema directory exists
    create_folder(SCHEMA_SAVE_PATH)

    # Construct the file path
    schema_file_path = os.path.join(SCHEMA_SAVE_PATH, f"{device.device_name}.json")
    #  
    # Save the schema as a JSON file
    try:
        save_json_file(schema_file_path, convert_model_to_json(device))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save device schema {e}")

    return {"message": f"Schema for {device.device_name} saved successfully!"}