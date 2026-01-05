"""
File management utilities for device schemas and data persistence.
"""
import json
import os
from typing import Any, Dict, Optional

from fastapi import HTTPException


def kafka_topic_name(device_id: str, run_id: str) -> str:
    """
    Generate a Kafka topic name from device and run IDs.
    
    Args:
        device_id: The device identifier
        run_id: The run identifier
        
    Returns:
        Formatted Kafka topic name
    """
    return f"{device_id}_{run_id}"


def create_folder(folder_path: str) -> None:
    """
    Create a folder if it does not exist.
    
    Args:
        folder_path: Path to the folder to create
    """
    os.makedirs(folder_path, exist_ok=True)


def save_json_file(file_path: str, data: Dict[str, Any]) -> None:
    """
    Save a dictionary as a JSON file.
    
    Args:
        file_path: Path where the JSON file will be saved
        data: Dictionary to save
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def convert_model_to_json(model: Any) -> Dict[str, Any]:
    """
    Convert a Pydantic model to a JSON-serializable dictionary.
    
    Args:
        model: Pydantic model instance
        
    Returns:
        Dictionary representation of the model
    """
    return json.loads(model.model_dump_json())


def load_json_file(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON file and return its content as a dictionary.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
        
    Raises:
        HTTPException: If file loading fails
    """
    try:
        with open(file_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {file_path}"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON in file {file_path}: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load JSON file: {e}"
        )


def device_exists(
    schema_path: str,
    device_name: str,
    raise_error_if_not_found: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Check if a device schema exists and optionally return it.
    
    Args:
        schema_path: Directory containing device schemas
        device_name: Name of the device to check
        raise_error_if_not_found: If True, raises HTTPException when device not found
        
    Returns:
        Device schema dictionary if found, None otherwise
        
    Raises:
        HTTPException: If device not found and raise_error_if_not_found is True
    """
    schema_file_path = os.path.join(schema_path, f"{device_name}.json")
    
    if os.path.exists(schema_file_path):
        return load_json_file(schema_file_path)
    
    if raise_error_if_not_found:
        raise HTTPException(
            status_code=404,
            detail=f"Device '{device_name}' not found."
        )
    
    return None


def validate_data(data: Dict[str, Any], schema: Dict[str, str]) -> bool:
    """
    Validate data against a schema definition.
    
    Args:
        data: Data dictionary to validate
        schema: Schema dictionary mapping field names to type strings
        
    Returns:
        True if data is valid, False otherwise
    """
    # Check for matching keys
    if set(data.keys()) != set(schema.keys()):
        return False

    type_mapping = {
        "float": (float, int),  # Allow int for float
        "int": (int,),
        "string": (str,),
    }

    for key, expected_type in schema.items():
        if key not in data:
            return False

        value = data[key]
        valid_types = type_mapping.get(expected_type)
        
        if valid_types is None:
            # Unsupported type in schema
            return False
            
        if not isinstance(value, valid_types):
            return False

    return True


def validate_schema_not_empty(register_device_json: Dict[str, Any]) -> None:
    """
    Validate that a device schema is not empty.
    
    Args:
        register_device_json: Device registration dictionary
        
    Raises:
        HTTPException: If schema is empty
    """
    schema = register_device_json.get("schema")
    if not schema or len(schema) == 0:
        raise HTTPException(
            status_code=400,
            detail="Schema cannot be empty."
        )
