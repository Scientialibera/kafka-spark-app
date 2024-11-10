import os
import json
from typing import Dict

from fastapi import HTTPException

def kafka_topic_name(device_id: str, run_id: str) -> str:
    """Returns the Kafka topic name based on the device_id and run_id."""
    return f"{device_id}_{run_id}"


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
    Prints expected vs. received data types for each key.
    Returns True if data is valid, False otherwise.
    """
    # Check for extra or missing keys
    if set(data.keys()) != set(schema.keys()):
        print("Mismatch in keys: ", f"Expected {set(schema.keys())}, but got {set(data.keys())}")
        return False

    for key, expected_data_type in schema.items():
        if key not in data:
            print(f"Missing key: {key} in data")
            return False

        received_value = data[key]
        received_data_type = type(received_value).__name__

        if expected_data_type == "float":
            if not isinstance(received_value, (float, int)):  # Allow int for float
                print(f"Key: '{key}', Expected: float, Received: {received_data_type}")
                return False
        elif expected_data_type == "int":
            if not isinstance(received_value, int):
                print(f"Key: '{key}', Expected: int, Received: {received_data_type}")
                return False
        elif expected_data_type == "string":
            if not isinstance(received_value, str):
                print(f"Key: '{key}', Expected: string, Received: {received_data_type}")
                return False
        else:
            # Unsupported data type in schema
            print(f"Key: '{key}' has an unsupported type: {expected_data_type}")
            return False

    # If all keys and data types match
    return True


def validate_schema_not_empty(register_device_json: Dict) -> None:
    """
    Checks if the schema dictionary is empty by validating its size.
    Raises an HTTPException if the dictionary is empty.

    Args:
        schema (Dict): The schema dictionary to check.

    Raises:
        HTTPException: If the schema is empty, raises a 400 status error with a specific message.
    """
    if not register_device_json.get('schema') or len(register_device_json.get('schema')) == 0:
        raise HTTPException(status_code=400, detail="Schema is empty.")
