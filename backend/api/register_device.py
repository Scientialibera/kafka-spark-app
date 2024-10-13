import json
import os
from fastapi import APIRouter, HTTPException

from backend.models.schemas import RegisterDeviceRequest
from utils.file_management import create_folder, save_json_file, convert_model_to_json, device_exists

router = APIRouter()


# Set the path where schemas will be saved
SCHEMA_SAVE_PATH = os.path.join("data", "device_schemas")  # Join with data/device_schemas path
REGISTER_DEVICE_ENDPOINT = "/register-device"
UPDATE_DEVICE_ENDPOINT = "/update-device"
DELETE_DEVICE_ENDPOINT = "/delete-device/{device_id}"
ALL_DEVICE_ENDPOINT = "/devices"
GET_DEVICE_ENDPOINT = "/device/{device_id}"


@router.post(REGISTER_DEVICE_ENDPOINT)
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


@router.put(UPDATE_DEVICE_ENDPOINT)
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


@router.delete(DELETE_DEVICE_ENDPOINT)
async def delete_device(device_id: str):
    # Check if the device exists and raise error if not found
    device_exists(SCHEMA_SAVE_PATH, device_id, raise_error_if_not_found=True)

    # Construct the file path and delete the file
    schema_file_path = os.path.join(SCHEMA_SAVE_PATH, f"{device_id}.json")
    try:
        os.remove(schema_file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete device schema: {e}")

    return {"message": f"Device '{device_id}' deleted successfully."}


@router.get(ALL_DEVICE_ENDPOINT)
async def get_all_devices():
    """Gets a list of all devices stored in the schema directory."""
    create_folder(SCHEMA_SAVE_PATH)  # Ensure folder exists
    
    devices = []
    try:
        for filename in os.listdir(SCHEMA_SAVE_PATH):
            if filename.endswith(".json"):
                devices.append(filename.replace(".json", ""))  # Remove .json extension
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list devices: {e}")
    
    return {"devices": devices}


@router.get(GET_DEVICE_ENDPOINT)
async def get_device_schema(device_id: str):
    """Get the schema for a specific device by ID."""
    device_schema = device_exists(SCHEMA_SAVE_PATH, device_id, raise_error_if_not_found=True)
    return {"device_name": device_id, "schema": device_schema}