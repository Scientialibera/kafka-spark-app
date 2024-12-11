import os
import json
import random
from datetime import datetime, timedelta

# Base folder path for devices (current directory)
BASE_DIR = os.getcwd()
RUN_COUNT = 15
PLAYER_COUNT = 10

# Duration of a football game in minutes
GAME_DURATION_MINUTES = 90

# Time interval in seconds (0.5 seconds)
INTERVAL_SECONDS = 0.5

# Temperature range (in degrees Celsius)
TEMPERATURE_RANGE = (36.0, 39.0)

# Function to generate synthetic temperature data
def generate_temperature_data(start_time, game_duration_minutes, interval_seconds):
    num_points = int((game_duration_minutes * 60) / interval_seconds)
    temperature_data = []
    timestamp = start_time

    for i in range(num_points):
        # Generate random temperature within the defined range
        temperature = round(random.uniform(*TEMPERATURE_RANGE), 2)

        # Format timestamp with alternating formats for full seconds and milliseconds
        if i % 2 == 0:
            formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

        temperature_data.append({
            "temperature": temperature,
            "timestamp": formatted_timestamp
        })

        timestamp += timedelta(seconds=interval_seconds)

    return temperature_data

# Function to randomly shorten the temperature data
def randomly_shorten_temperature_data(temperature_data):
    # Decide the percentage of data to keep (between 50% and 100%)
    keep_percentage = random.uniform(0.5, 1.0)
    num_points_to_keep = int(len(temperature_data) * keep_percentage)
    return temperature_data[:num_points_to_keep]

# Main function to clean and create temperature files
def clean_and_create_temperature_files():
    for player_num in range(1, PLAYER_COUNT + 1):
        player_folder = f"player_temperature_{player_num}"
        player_folder_path = os.path.join(BASE_DIR, player_folder)

        # Create player_temperature_X folder if it doesn't exist
        os.makedirs(player_folder_path, exist_ok=True)

        for run_num in range(1, RUN_COUNT + 1):
            run_folder = f"run_{str(run_num).zfill(3)}"
            run_folder_path = os.path.join(player_folder_path, run_folder)

            # Create run folder if it doesn't exist
            os.makedirs(run_folder_path, exist_ok=True)

            # Delete all temperature JSON files in the run folder
            for file in os.listdir(run_folder_path):
                if file.endswith(".json"):
                    os.remove(os.path.join(run_folder_path, file))

            # Create the correct temperature JSON file named after the parent player_temperature_X folder
            temp_filename = f"{player_folder}.json"
            temp_file_path = os.path.join(run_folder_path, temp_filename)

            # Generate synthetic temperature data for up to 90 minutes
            start_time = datetime.now()
            temperature_data = generate_temperature_data(start_time, GAME_DURATION_MINUTES, INTERVAL_SECONDS)

            # Randomly shorten the temperature data
            shortened_temperature_data = randomly_shorten_temperature_data(temperature_data)

            # Write data to the JSON file
            with open(temp_file_path, "w") as file:
                json.dump(shortened_temperature_data, file, indent=4)

            print(f"Created {temp_file_path}")

if __name__ == "__main__":
    clean_and_create_temperature_files()
