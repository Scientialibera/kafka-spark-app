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

# Time interval in seconds (between 5 and 30 seconds for heart rate data)
INTERVAL_RANGE_SECONDS = (5, 30)

# Heart rate range (in beats per minute)
HEART_RATE_RANGE = (120, 180)

# Function to generate synthetic heart rate data
def generate_heart_rate_data(start_time, game_duration_minutes):
    total_seconds = game_duration_minutes * 60
    elapsed_time = 0
    heart_rate_data = []
    timestamp = start_time

    while elapsed_time < total_seconds:
        # Generate random heart rate within the defined range
        heart_rate = random.randint(*HEART_RATE_RANGE)

        # Format timestamp with alternating formats for full seconds and milliseconds
        if len(heart_rate_data) % 2 == 0:
            formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            formatted_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]

        heart_rate_data.append({
            "heart_rate": heart_rate,
            "timestamp": formatted_timestamp
        })

        # Increment the timestamp by a random interval within the range
        interval_seconds = random.randint(*INTERVAL_RANGE_SECONDS)
        timestamp += timedelta(seconds=interval_seconds)
        elapsed_time += interval_seconds

    return heart_rate_data

# Function to randomly shorten the heart rate data
def randomly_shorten_heart_rate_data(heart_rate_data):
    # Decide the percentage of data to keep (between 50% and 100%)
    keep_percentage = random.uniform(0.5, 1.0)
    num_points_to_keep = int(len(heart_rate_data) * keep_percentage)
    return heart_rate_data[:num_points_to_keep]

# Main function to clean and create heart rate files
def clean_and_create_heart_rate_files():
    for player_num in range(1, PLAYER_COUNT + 1):
        player_folder = f"player_heart_rate_{player_num}"
        player_folder_path = os.path.join(BASE_DIR, player_folder)

        # Create player_heart_rate_X folder if it doesn't exist
        os.makedirs(player_folder_path, exist_ok=True)

        for run_num in range(1, RUN_COUNT + 1):
            run_folder = f"run_{str(run_num).zfill(3)}"
            run_folder_path = os.path.join(player_folder_path, run_folder)

            # Create run folder if it doesn't exist
            os.makedirs(run_folder_path, exist_ok=True)

            # Delete all heart rate JSON files in the run folder
            for file in os.listdir(run_folder_path):
                if file.endswith(".json"):
                    os.remove(os.path.join(run_folder_path, file))

            # Create the correct heart rate JSON file named after the parent player_heart_rate_X folder
            hr_filename = f"{player_folder}.json"
            hr_file_path = os.path.join(run_folder_path, hr_filename)

            # Generate synthetic heart rate data for up to 90 minutes
            start_time = datetime.now()
            heart_rate_data = generate_heart_rate_data(start_time, GAME_DURATION_MINUTES)

            # Randomly shorten the heart rate data
            shortened_heart_rate_data = randomly_shorten_heart_rate_data(heart_rate_data)

            # Write data to the JSON file
            with open(hr_file_path, "w") as file:
                json.dump(shortened_heart_rate_data, file, indent=4)

            print(f"Created {hr_file_path}")

if __name__ == "__main__":
    clean_and_create_heart_rate_files()
