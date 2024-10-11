import os
import json

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