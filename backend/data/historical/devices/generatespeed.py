import os
import json
import random
from datetime import datetime, timedelta

# Base folder path for devices (current directory)
BASE_DIR = os.getcwd()
RUN_COUNT = 15
DEVICE_COUNT = 10

# Duration of a football game in minutes
GAME_DURATION_MINUTES = 90

# Time interval in seconds (0.5 seconds)
INTERVAL_SECONDS = 0.5

# Speed value ranges (updated ranges for more variability)
SPEED_X_RANGE = (0, 12)  # Increased upper bound
SPEED_Y_RANGE = (0, 12)
SPEED_Z_RANGE = (0, 5)   # More limited Z variation

# Function to generate synthetic speed data with variability patterns
def generate_speed_data(start_time, game_duration_minutes, interval_seconds):
    num_points = int((game_duration_minutes * 60) / interval_seconds)
    speed_data = []
    timestamp = start_time

    for i in range(num_points):
        # Introduce variability patterns by alternating high and low speed phases
        phase = i // 300  # Each phase lasts 300 intervals (~2.5 minutes)
        if phase % 2 == 0:
            # Higher speeds in this phase
            speed_x = round(random.uniform(5, 12), 2)
            speed_y = round(random.uniform(5, 12), 2)
        else:
            # Lower speeds in this phase
            speed_x = round(random.uniform(0, 6), 2)
            speed_y = round(random.uniform(0, 6), 2)

        # Random Z speed within the defined range
        speed_z = round(random.uniform(*SPEED_Z_RANGE), 2)

        # Random small modifiers for additional variability
        speed_x += round(random.uniform(-1, 1), 2)
        speed_y += round(random.uniform(-1, 1), 2)
        speed_z += round(random.uniform(-0.5, 0.5), 2)

        # Ensure speeds are not negative
        speed_x = max(speed_x, 0)
        speed_y = max(speed_y, 0)
        speed_z = max(speed_z, 0)

        # Format timestamp with milliseconds
        formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

        speed_data.append({
            "speed_x": speed_x,
            "speed_y": speed_y,
            "speed_z": speed_z,
            "timestamp": formatted_timestamp
        })

        timestamp += timedelta(seconds=interval_seconds)

    return speed_data

# Function to randomly shorten the speed data
def randomly_shorten_speed_data(speed_data):
    # Decide the percentage of data to keep (between 50% and 100%)
    keep_percentage = random.uniform(0.5, 1.0)
    num_points_to_keep = int(len(speed_data) * keep_percentage)
    return speed_data[:num_points_to_keep]

# Main function to clean and create speed files
def clean_and_create_speed_files():
    for device_num in range(1, DEVICE_COUNT + 1):
        speed_folder = f"speed_{device_num}"
        speed_folder_path = os.path.join(BASE_DIR, speed_folder)

        # Create speed_X folder if it doesn't exist
        os.makedirs(speed_folder_path, exist_ok=True)

        for run_num in range(1, RUN_COUNT + 1):
            run_folder = f"run_{str(run_num).zfill(3)}"
            run_folder_path = os.path.join(speed_folder_path, run_folder)

            # Create run folder if it doesn't exist
            os.makedirs(run_folder_path, exist_ok=True)

            # Delete all speed JSON files in the run folder
            for file in os.listdir(run_folder_path):
                if file.endswith(".json"):
                    os.remove(os.path.join(run_folder_path, file))

            # Create the correct speed JSON file named after the parent speed_X folder
            speed_filename = f"{speed_folder}.json"
            speed_file_path = os.path.join(run_folder_path, speed_filename)

            # Generate synthetic speed data for up to 90 minutes
            start_time = datetime.now()
            speed_data = generate_speed_data(start_time, GAME_DURATION_MINUTES, INTERVAL_SECONDS)

            # Randomly shorten the speed data
            shortened_speed_data = randomly_shorten_speed_data(speed_data)

            # Write data to the JSON file
            with open(speed_file_path, "w") as file:
                json.dump(shortened_speed_data, file, indent=4)

            print(f"Created {speed_file_path}")

if __name__ == "__main__":
    clean_and_create_speed_files()
