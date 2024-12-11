import os
import json
import random

# Base folder path for devices (current directory)
BASE_DIR = os.getcwd()
RUN_COUNT = 15

# Latitude and Longitude Adjustment Range
LATITUDE_ADJUSTMENT_RANGE = (-0.0002, 0.0002)
LONGITUDE_ADJUSTMENT_RANGE = (-0.0002, 0.0002)

# Base GPS file path from gps_1/run_001/gps_1.json
BASE_GPS_FILE = os.path.join(BASE_DIR, "gps_1", "run_001", "gps_1.json")

# Function to adjust latitude and longitude
def adjust_coordinates(latitude, longitude):
    new_latitude = latitude + random.uniform(*LATITUDE_ADJUSTMENT_RANGE)
    new_longitude = longitude + random.uniform(*LONGITUDE_ADJUSTMENT_RANGE)
    return round(new_latitude, 14), round(new_longitude, 14)

# Function to randomly shorten the GPS data
def randomly_shorten_gps_data(gps_data):
    # Decide the percentage of data to keep (between 50% and 100%)
    keep_percentage = random.uniform(0.5, 1.0)
    num_points_to_keep = int(len(gps_data) * keep_percentage)
    return gps_data[:num_points_to_keep]

# Main function to clean and create GPS files
def clean_and_create_gps_files():
    # Check if the base GPS file exists
    if not os.path.isfile(BASE_GPS_FILE):
        print(f"Base file not found: {BASE_GPS_FILE}")
        return

    # Load the base GPS data once
    with open(BASE_GPS_FILE, "r") as file:
        base_gps_data = json.load(file)

    for gps_folder in [f for f in os.listdir(BASE_DIR) if f.startswith("gps") and os.path.isdir(os.path.join(BASE_DIR, f))]:
        gps_folder_path = os.path.join(BASE_DIR, gps_folder)

        for run_num in range(1, RUN_COUNT + 1):
            run_folder = f"run_{str(run_num).zfill(3)}"
            run_folder_path = os.path.join(gps_folder_path, run_folder)

            # Create run folder if it doesn't exist
            os.makedirs(run_folder_path, exist_ok=True)

            # Delete all GPS JSON files in the run folder
            for file in os.listdir(run_folder_path):
                if file.endswith(".json"):
                    os.remove(os.path.join(run_folder_path, file))

            # Create the correct GPS JSON file named after the parent gps_X folder
            gps_filename = f"{gps_folder}.json"
            gps_file_path = os.path.join(run_folder_path, gps_filename)

            # Adjust GPS data (keep timestamps, change lat/lon)
            adjusted_gps_data = []
            for entry in base_gps_data:
                new_lat, new_lon = adjust_coordinates(entry["latitude"], entry["longitude"])
                adjusted_gps_data.append({
                    "latitude": new_lat,
                    "longitude": new_lon,
                    "timestamp": entry["timestamp"]
                })

            # Randomly shorten the GPS data
            shortened_gps_data = randomly_shorten_gps_data(adjusted_gps_data)

            # Write adjusted data to the JSON file
            with open(gps_file_path, "w") as file:
                json.dump(shortened_gps_data, file, indent=4)

            print(f"Created {gps_file_path}")

if __name__ == "__main__":
    clean_and_create_gps_files()
