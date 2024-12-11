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

# Acceleration range (in meters per second squared)
ACCELERATION_RANGE = (-10.0, 10.0)

# Function to generate synthetic acceleration data
def generate_acceleration_data(start_time, game_duration_minutes, interval_seconds):
    num_points = int((game_duration_minutes * 60) / interval_seconds)
    acceleration_data = []
    timestamp = start_time

    for i in range(num_points):
        # Generate random acceleration values within the defined range
        acceleration_x = round(random.uniform(*ACCELERATION_RANGE), 2)
        acceleration_y = round(random.uniform(*ACCELERATION_RANGE), 2)
        acceleration_z = round(random.uniform(*ACCELERATION_RANGE), 2)

        # Format timestamp with alternating formats for full seconds and milliseconds
        if i % 2 == 0:
            formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

        acceleration_data.append({
            "acceleration_x": acceleration_x,
            "acceleration_y": acceleration_y,
            "acceleration_z": acceleration_z,
            "timestamp": formatted_timestamp
        })

        # Increment the timestamp by the interval
        timestamp += timedelta(seconds=interval_seconds)

    return acceleration_data

# Function to randomly shorten the acceleration data
def randomly_shorten_acceleration_data(acceleration_data):
    # Decide the percentage of data to keep (between 50% and 100%)
    keep_percentage = random.uniform(0.5, 1.0)
    num_points_to_keep = int(len(acceleration_data) * keep_percentage)
    return acceleration_data[:num_points_to_keep]

# Main function to clean and create acceleration files
def clean_and_create_acceleration_files():
    for player_num in range(1, PLAYER_COUNT + 1):
        player_folder = f"accel_{player_num}"
        player_folder_path = os.path.join(BASE_DIR, player_folder)

        # Create accel_X folder if it doesn't exist
        os.makedirs(player_folder_path, exist_ok=True)

        for run_num in range(1, RUN_COUNT + 1):
            run_folder = f"run_{str(run_num).zfill(3)}"
            run_folder_path = os.path.join(player_folder_path, run_folder)

            # Create run folder if it doesn't exist
            os.makedirs(run_folder_path, exist_ok=True)

            # Delete all acceleration JSON files in the run folder
            for file in os.listdir(run_folder_path):
                if file.endswith(".json"):
                    os.remove(os.path.join(run_folder_path, file))

            # Create the correct acceleration JSON file named after the parent accel_X folder
            accel_filename = f"{player_folder}.json"
            accel_file_path = os.path.join(run_folder_path, accel_filename)

            # Generate synthetic acceleration data for up to 90 minutes
            start_time = datetime.now()
            acceleration_data = generate_acceleration_data(start_time, GAME_DURATION_MINUTES, INTERVAL_SECONDS)

            # Randomly shorten the acceleration data
            shortened_acceleration_data = randomly_shorten_acceleration_data(acceleration_data)

            # Write data to the JSON file
            with open(accel_file_path, "w") as file:
                json.dump(shortened_acceleration_data, file, indent=4)

            print(f"Created {accel_file_path}")

if __name__ == "__main__":
    clean_and_create_acceleration_files()
