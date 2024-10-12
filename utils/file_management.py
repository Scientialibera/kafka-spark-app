import os
import json
from fastapi import HTTPException

def create_folder(folder_path: str):
    """Create a folder if it does not exist."""
    os.makedirs(folder_path, exist_ok=True)


def save_json_file(file_path: str, data: dict):
    """Save a dictionary as a JSON file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def convert_model_to_json(model):
    """Convert a Pydantic model to a JSON serializable dictionary."""
    return json.loads(model.model_dump_json())


def load_json_file(file_path: str):
    """Loads a JSON file and returns its content as a dictionary."""
    try:
        with open(file_path, "r") as json_file:
            return json.load(json_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load JSON file: {e}")


def device_exists(schema_path: str, device_name: str, raise_error_if_not_found: bool = False):
    """
    Checks if a device with the given name exists and returns the schema if it does.
    Optionally raises an HTTPException if the device is not found.
    """
    schema_file_path = os.path.join(schema_path, f"{device_name}.json")
    
    if os.path.exists(schema_file_path):
        return load_json_file(schema_file_path)
    
    if raise_error_if_not_found:
        raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found.")
    
    return None