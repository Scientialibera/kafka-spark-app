import json
import os
from fastapi import APIRouter, HTTPException

from backend.models.schemas import RegisterDeviceRequest
from utils.file_management import create_folder, save_json_file, convert_model_to_json, device_exists

router = APIRouter()


# Set the path where schemas will be saved
SCHEMA_SAVE_PATH = os.path.join("data", "device_schemas")  # Join with data/device_schemas path


@router.post("/register-device")
async def register_device_schema(device: RegisterDeviceRequest):
    # Ensure the schema directory exists
    create_folder(SCHEMA_SAVE_PATH)

    # Check if the device already exists
    existing_device_schema = device_exists(SCHEMA_SAVE_PATH, device.device_name)
    
    if existing_device_schema:
        # Check if the schema is the same
        if existing_device_schema == convert_model_to_json(device):
            return {"message": f"Device '{device.device_name}' already exists with the same schema."}
        else:
            raise HTTPException(status_code=400, detail="Existing device with different schema, use update endpoint.")
    
    # If no device exists, save the new schema
    schema_file_path = os.path.join(SCHEMA_SAVE_PATH, f"{device.device_name}.json")
    try:
        save_json_file(schema_file_path, convert_model_to_json(device))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save device schema {e}")

    return {"message": f"Schema for {device.device_name} saved successfully!"}


@router.put("/update-device")
async def update_device_schema(device: RegisterDeviceRequest):
    # Ensure the schema directory exists
    create_folder(SCHEMA_SAVE_PATH)

    # Check if the device already exists
    existing_device_schema = device_exists(SCHEMA_SAVE_PATH, device.device_name)

    if not existing_device_schema:
        raise HTTPException(status_code=400, detail="Device not found. Use /register-device to create a new device.")
    
    # If the schema exists, save the new schema (updating the device)
    schema_file_path = os.path.join(SCHEMA_SAVE_PATH, f"{device.device_name}.json")
    try:
        save_json_file(schema_file_path, convert_model_to_json(device))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update device schema: {e}")

    return {"message": f"Schema for {device.device_name} updated successfully!"}