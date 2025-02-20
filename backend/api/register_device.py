import json
import os
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException

from backend.models.schemas import RegisterDeviceRequest
from utils.file_management import (
    create_folder,
    save_json_file,
    convert_model_to_json,
    device_exists,
    validate_schema_not_empty
)
from backend.config.config import SCHEMA_DATA_PATH

router = APIRouter()


# Set the path where schemas will be saved
SCHEMA_SAVE_PATH = SCHEMA_DATA_PATH  # Join with data/device_schemas path

REGISTER_DEVICE_ENDPOINT: str = "/register-device"
UPDATE_DEVICE_ENDPOINT: str = "/update-device"
DELETE_DEVICE_ENDPOINT: str = "/delete-device/{device_id}"
ALL_DEVICE_ENDPOINT: str = "/devices"
GET_DEVICE_ENDPOINT: str = "/device/{device_id}"


@router.post(REGISTER_DEVICE_ENDPOINT)
async def register_device_schema(
    device: RegisterDeviceRequest,
) -> Dict[str, str]:
    """
    Endpoint allows the registration of a new device schema. It ensures that the schema directory exists,
    checks for existing devices, and saves the new schema if it doesn't already exist.

    Args:
        device (RegisterDeviceRequest): The device registration request containing device details and schema.

    Returns:
        Dict[str, str]: A message indicating the result of the registration process.

    Raises:
        HTTPException: If the device already exists with a different schema or if saving the schema fails.
    """
    # Ensure the schema directory exists
    create_folder(SCHEMA_SAVE_PATH)

    # Check if the device already exists
    existing_device_schema: Optional[Dict] = device_exists(
        SCHEMA_SAVE_PATH, device.device_name
    )

    if existing_device_schema:
        # Check if the existing schema matches the new schema
        if existing_device_schema == convert_model_to_json(device):
            return {
                "message": f"Device '{device.device_name}' already exists with the same schema."
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Existing device with different schema, use update endpoint.",
            )

    # Save the new device schema
    schema_file_path: str = os.path.join(
        SCHEMA_SAVE_PATH, f"{device.device_name}.json"
    )
    try:
        device_schema = convert_model_to_json(device)
        validate_schema_not_empty(device_schema)
        save_json_file(schema_file_path, device_schema)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save device schema: {e}"
        )

    return {"message": f"Schema for {device.device_name} saved successfully!"}


@router.put(UPDATE_DEVICE_ENDPOINT)
async def update_device_schema(
    device: RegisterDeviceRequest,
) -> Dict[str, str]:
    """
    Endpoint updates the schema of an existing device. It ensures the schema directory exists,
    verifies the device's existence, and updates the schema accordingly.

    Args:
        device (RegisterDeviceRequest): The device update request containing updated device details and schema.

    Returns:
        Dict[str, str]: A message indicating the result of the update process.

    Raises:
        HTTPException: If the device does not exist or if updating the schema fails.
    """
    # Ensure the schema directory exists
    create_folder(SCHEMA_SAVE_PATH)

    # Check if the device exists
    existing_device_schema: Optional[Dict] = device_exists(
        SCHEMA_SAVE_PATH, device.device_name
    )

    if not existing_device_schema:
        raise HTTPException(
            status_code=400,
            detail="Device not found. Use /register-device to create a new device.",
        )

    # Update the existing device schema
    schema_file_path: str = os.path.join(
        SCHEMA_SAVE_PATH, f"{device.device_name}.json"
    )
    try:
        device_schema = convert_model_to_json(device)
        validate_schema_not_empty(device_schema)

        save_json_file(schema_file_path, device_schema)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update device schema: {e}"
        )

    return {"message": f"Schema for {device.device_name} updated successfully!"}


@router.delete(DELETE_DEVICE_ENDPOINT)
async def delete_device(device_id: str) -> Dict[str, str]:
    """
    Endpoint deletes the schema of a specified device. It verifies the device's existence before deletion.

    Args:
        device_id (str): The ID of the device to be deleted.

    Returns:
        Dict[str, str]: A message indicating the result of the deletion process.

    Raises:
        HTTPException: If the device does not exist or if deletion fails.
    """
    # Verify the device exists
    device_exists(SCHEMA_SAVE_PATH, device_id, raise_error_if_not_found=True)

    # Construct the file path and delete the schema file
    schema_file_path: str = os.path.join(SCHEMA_SAVE_PATH, f"{device_id}.json")
    try:
        os.remove(schema_file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete device schema: {e}"
        )

    return {"message": f"Device '{device_id}' deleted successfully."}


@router.get(ALL_DEVICE_ENDPOINT)
async def get_all_devices() -> Dict[str, List[str]]:
    """
    Endpoint fetches and returns all device names stored in the schema directory.

    Returns:
        Dict[str, List[str]]: A dictionary containing a list of all device names.

    Raises:
        HTTPException: If listing devices fails.
    """
    # Ensure the schema directory exists
    create_folder(SCHEMA_SAVE_PATH)

    devices: List[str] = []
    try:
        for filename in os.listdir(SCHEMA_SAVE_PATH):
            if filename.endswith(".json"):
                devices.append(filename.replace(".json", ""))  # Remove .json extension
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list devices: {e}"
        )

    return {"devices": devices}


@router.get(GET_DEVICE_ENDPOINT)
async def get_device_schema(device_id: str) -> Dict[str, object]:
    """
    Endpoint fetches and returns the schema of the specified device.

    Args:
        device_id (str): The ID of the device whose schema is to be retrieved.

    Returns:
        Dict[str, object]: A dictionary containing the device name and its schema.

    Raises:
        HTTPException: If the device does not exist or if retrieval fails.
    """
    # Retrieve the device schema
    device_schema: Dict = device_exists(
        SCHEMA_SAVE_PATH, device_id, raise_error_if_not_found=True
    )

    return {"device_name": device_id, "schema": device_schema}