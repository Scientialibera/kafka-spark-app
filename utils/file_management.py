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

def validate_data(data: dict, schema: dict) -> bool:
    """
    Validates the data against the provided schema.
    Returns True if data is valid, False otherwise.
    """
    # Check for extra or missing keys
    if set(data.keys()) != set(schema.keys()):
        return False

    for key, data_type in schema.items():
        if key not in data:
            return False

        if data_type == "float":
            if not isinstance(data[key], (float, int)):
                return False
        elif data_type == "int":
            if not isinstance(data[key], int):
                return False
        elif data_type == "string":
            if not isinstance(data[key], str):
                return False
        else:
            # Unsupported data type
            return False

    return True