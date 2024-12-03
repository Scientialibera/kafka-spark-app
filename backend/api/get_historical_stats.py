import json
import os
import datetime
from utils.maths_functions import haversine_distance
import math
from datetime import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter()


# Set the path relative to one folder above the current script's directory
# Navigate two levels up to reach 'sports_project-main'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Move up one level
HISTORICAL_DATA_PATH = os.path.join(BASE_DIR, "data", "historical", "devices")  # Correct relative path

# Endpoint 1: Team Statistics (Line Chart)
@router.get("/team-statistics")
def get_team_statistics():
    """
    Endpoint to fetch team statistics (Line Chart Data).
    """
    try:
        metrics = calculate_metrics()
        return {
            "Total Distance Per Game": metrics["Team Metrics"]["Total Distance Per Game"],
            "Average Speed Per Game": metrics["Team Metrics"]["Average Team Speed"],
            "Max Speed Per Game": metrics["Team Metrics"]["Max Team Speed"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 2: Wins/Losses/Draws
@router.get("/game-statistics")
def get_game_statistics():
    """
    Endpoint to fetch wins, losses, and draws.
    """
    # dummy data for wins losses and draws can be adjusted
    game_statistics = {
        "Wins": 12,
        "Losses": 5,
        "Draws": 3,
    }
    return game_statistics


# Endpoint 3: Total Distance/Game and Recovery
@router.get("/team-metrics")
def get_team_metrics():
    """
    Endpoint to fetch total distance per game and recovery metrics.
    """
    try:
        metrics = calculate_metrics()
        return {
            "Total Distance Per Game": metrics["Team Metrics"]["Average Distance Per Game"],
            "Average Team Recovery Rate": metrics["Team Metrics"]["Average Team Recovery Rate"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 4: Player Overview Table
@router.get("/player-overview/{player_id}")
def get_player_overview(player_id: int):
    """
    Endpoint to fetch player-specific metrics for the overview table.
    """
    try:
        metrics = calculate_metrics()
        player_metrics = metrics["Player Metrics"].get(player_id, None)
        if not player_metrics:
            raise HTTPException(status_code=404, detail="Player data not found.")
        return player_metrics
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 5: Fatigue Level Distribution
@router.get("/fatigue-distribution")
def get_fatigue_distribution():
    """
    Endpoint to fetch fatigue level distribution across players.
    """
    try:
        metrics = calculate_metrics()
        fatigue_levels = metrics["Recommendations"]["Player Recommendations"]
        distribution = {
            "Low Fatigue": sum(1 for recs in fatigue_levels.values() if "Low" in recs),
            "Medium Fatigue": sum(1 for recs in fatigue_levels.values() if "Medium" in recs),
            "High Fatigue": sum(1 for recs in fatigue_levels.values() if "High" in recs),
        }
        return distribution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint 6: All Players Recommendations
@router.get("/recommendations")
def get_recommendations():
    """
    Endpoint to fetch recommendations for all players and the team.
    """
    try:
        metrics = calculate_metrics()
        return metrics["Recommendations"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_metrics():
    """

    It calculates all required metrics and then adds recommendations for players
    
    returns:
        Dictionary: A dictionary containing all calculated metrics and recommendations

    """
    # Team-related metrics
    team_distance = c_team_distance()  # Total and average distance per game
    average_team_speed, max_team_speed = team_speeds()  # Speed metrics
    player_heart_rate_recovery, average_team_recovery_rate = heart_rate_recovery()  # Recovery metrics
    fatigue_levels = calculate_fatigue_levels()  # Fatigue levels for players and team
    injury_data = injuries()  # Injury data (total and per player)

    # Player-specific metrics
    player_metrics = {}  # Store individual player metrics
    for player_id, recovery_data in player_heart_rate_recovery.items():
        # Combine recovery data with other metrics
        player_metrics[player_id] = {
            "Heart Rate Recovery Rate": recovery_data.get("Recovery Rate (BPM/Sec)", None),
            "Fatigue Level": fatigue_levels["Fatigue Levels Per Player"][player_id]["Fatigue Level"],
            "Injuries": injury_data["Injuries Per Player"][player_id]["Total Injuries"],
        }

    # Recommendations
    player_recommendations = {}
    team_recommendations = []

    for player_id, metrics in player_metrics.items():
        recommendations = []

        # Fatigue level recommendations
        if metrics["Fatigue Level"] == "High":
            recommendations.append("It's Recommended to rest or lighter training to reduce fatigue.")
        elif metrics["Fatigue Level"] == "Medium":
            recommendations.append("Please Monitor workload and adjust training intensity if needed.")



        # Heart rate recovery recommendations
        if metrics.get("Heart Rate Recovery Rate") and metrics["Heart Rate Recovery Rate"] > 0.5:
            recommendations.append("Improve cardiovascular fitness with aerobic training.")


        # Injuries recommendations
        if metrics.get("Injuries", 0) > 3:
            recommendations.append("High injury count - please consider medical check-up or reduced workload.")




        # Distance trend recommendations
        if metrics.get("Average Distance Trend") == "Decreasing":
            recommendations.append("Endurance training recommended to improve distance trends.")

        player_recommendations[player_id] = recommendations

    # Generate team-wide recommendations
    fatigue_counts = fatigue_levels["Total Fatigue Levels"]
    if fatigue_counts["High"] > 3:  # Threshold: more than 3 players with high fatigue
        team_recommendations.append("Reduce overall training intensity due to high team fatigue.")

    if injury_data["Total Injuries"] > 5:  # Threshold: more than 5 injuries in total
        team_recommendations.append("Focus on medical assessment and injury prevention strategies.")

    if average_team_recovery_rate > 0.5:
        team_recommendations.append("Team-wide cardiovascular training recommended to improve recovery rates.")

    # all metrics and recommendations
    return {
        "Team Metrics": {
            "Total Distance Per Game": team_distance["Total Distance Per Game"],
            "Average Distance Per Game": team_distance["Average Distance Per Game"],
            "Average Team Speed": average_team_speed,
            "Max Team Speed": max_team_speed,
            "Average Team Recovery Rate": average_team_recovery_rate,
        },
        "Player Metrics": player_metrics,
        "Recommendations": {
            "Player Recommendations": player_recommendations,
            "Team Recommendations": team_recommendations,
        },
    }


def c_team_distance():
    """

    It calculates the total and average distance run per game as well as for all players

    """
    game_distances = {}  

    for player_id in range(1, 11):  # for 10 players
        gps_path = os.path.join(HISTORICAL_DATA_PATH, f"gps_{player_id}")
        for run_path in os.listdir(gps_path):  # loop all games
            if run_path == '.DS_Store':  # Skip system files
                continue
            run_file_path = os.path.join(gps_path, run_path, f"gps_{player_id}.json")
            with open(run_file_path, 'r') as file:
                data = json.load(file)
            run_distance = 0
            for i in range(len(data) - 1):
                point1 = data[i]
                point2 = data[i + 1]
                run_distance += haversine_distance(
                    lat1=point1["latitude"],
                    lon1=point1["longitude"],
                    lat2=point2["latitude"],
                    lon2=point2["longitude"],
                )



            if run_path not in game_distances:
                game_distances[run_path] = 0
            game_distances[run_path] += run_distance

    total_games = len(game_distances)
    average_distances_per_game = {
        game: round(total_distance / 10, 2)  # Divide by # of players
        for game, total_distance in game_distances.items()
    }

    return {
        "Total Distance Per Game": {game: round(distance, 2) for game, distance in game_distances.items()},
        "Average Distance Per Game": average_distances_per_game,
    }

def team_speeds():
    """

    It calculates average speed (km/h) and max team speed taking into account x,y,z coordinates

    """


    total_speeds = []
    for player_id in range(1, 2):  # for 10 players
        speed_path = os.path.join(HISTORICAL_DATA_PATH, f"speed_{player_id}")
        for run_path in os.listdir(speed_path):  # loop 15 games
            run_file_path = os.path.join(speed_path, run_path, f"speed_{player_id}.json")
            with open(run_file_path, 'r') as file:
                data = json.load(file)
            for entry in data:
                speed_x = entry["schema"]["speed_x"]
                speed_y = entry["schema"]["speed_y"]
                speed_z = entry["schema"]["speed_z"]

                # Calculate the final vector of speed
                speed_magnitude = math.sqrt(speed_x**2 + speed_y**2 + speed_z**2)
                total_speeds.append(speed_magnitude)

    if total_speeds:
        average_speed = round(sum(total_speeds) / len(total_speeds), 2)
        max_speed = round(max(total_speeds), 2)
    else:
        average_speed = 0
        max_speed = 0

    return average_speed, max_speed

def parse_timestamp(timestamp):
    """
    Parse a simpling timestamp string into a datetime object, supporting both formats
    with and without microseconds.


    """
    try:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")


def heart_rate_recovery():
    """

    It calculates the average heart rate recovery (beats per min) per player and for team
    Returns average player recovery rate and also team recovery rate.

    """

    player_averages = {} 
    total_team_recovery_rate = 0
    team_recovery_count = 0

    for player_id in range(1, 11): # for 10 players
        heart_rate_path = os.path.join(HISTORICAL_DATA_PATH, f"player_heart_rate_{player_id}")
        
        # initialize metrics for players
        total_heart_rate = 0
        absolute_max_heart_rate = 0
        total_recovery_rate = 0
        run_count = 0
        heart_rate_count = 0
        
        for run_path in os.listdir(heart_rate_path):
            if run_path == '.DS_Store':  # Skip system files
                continue
            run_file_path = os.path.join(heart_rate_path, run_path, f"player_heart_rate_{player_id}.json")
            with open(run_file_path, 'r') as file:
                data = json.load(file)

            max_heart_rate = 0
            max_heart_rate_timestamp = None
            heart_rate_drop_60s = None

            run_total_heart_rate = 0
            run_heart_rate_count = 0

            for entry in data:
                heart_rate = entry["schema"]["heart_rate"]
                run_total_heart_rate += heart_rate
                run_heart_rate_count += 1
                


                timestamp = parse_timestamp(entry["schema"]["timestamp"])
                if heart_rate > max_heart_rate:
                    max_heart_rate = heart_rate
                    max_heart_rate_timestamp = timestamp
                
                # Update absolute max if this heart rate is higher
                if heart_rate > absolute_max_heart_rate:
                    absolute_max_heart_rate = heart_rate

            # heart rate drop after 60s
            if max_heart_rate_timestamp:
                for entry in data:
                    heart_rate = entry["schema"]["heart_rate"]
                    timestamp = parse_timestamp(entry["schema"]["timestamp"])
                    time_diff = (timestamp - max_heart_rate_timestamp).total_seconds()

                    if 1 <= time_diff <= 60:  # Check if within 60 seconds
                        heart_rate_drop_60s = max_heart_rate - heart_rate

            # Accumulate totals for this run
            if run_heart_rate_count > 0:
                total_heart_rate += run_total_heart_rate
                heart_rate_count += run_heart_rate_count
                
                if heart_rate_drop_60s is not None:
                    recovery_rate = round(heart_rate_drop_60s / 60, 2)
                    total_recovery_rate += recovery_rate
                    total_team_recovery_rate += recovery_rate
                    team_recovery_count += 1
                
                run_count += 1

        # Calculate averages for this player
        if run_count > 0:
            player_averages[player_id] = {
                "Average Heart Rate": round(total_heart_rate / heart_rate_count, 2),
                "Overall Maximum Heart Rate": absolute_max_heart_rate,
                "Average Recovery Rate (BPM/Sec)": round(total_recovery_rate / run_count, 2),
            }

    average_team_recovery_rate = round(total_team_recovery_rate / team_recovery_count, 2) if team_recovery_count > 0 else None

    return player_averages, average_team_recovery_rate

def calculate_average_heart_rate():
    """
    
    It calculates average heart rate for every player overall and for each game
    


    """
    player_heart_rate_data = {}  # Store data for each player
    for player_id in range(1, 11):  # Loop over 10 players
        heart_rate_path = os.path.join(HISTORICAL_DATA_PATH, f"player_heart_rate_{player_id}")
        total_heart_rate = 0
        total_readings = 0
        game_heart_rates = {}

        for run_path in os.listdir(heart_rate_path):  # Loop over runs
            if run_path == '.DS_Store':
                continue
            run_file_path = os.path.join(heart_rate_path, run_path, f"player_heart_rate_{player_id}.json")
            with open(run_file_path, 'r') as file:
                data = json.load(file)

            game_total = 0
            game_count = 0
            for entry in data:
                heart_rate = entry["schema"]["heart_rate"]
                game_total += heart_rate
                total_heart_rate += heart_rate
                game_count += 1
                total_readings += 1

            # Average for this game
            game_heart_rates[run_path] = round(game_total / game_count, 2) if game_count > 0 else 0

        # Average for this player for all the games
        player_heart_rate_data[player_id] = {
            "Total Average Heart Rate": round(total_heart_rate / total_readings, 2) if total_readings > 0 else 0,
            "Per Game Average Heart Rate": game_heart_rates,
        }



    return player_heart_rate_data

def injuries():
    """
    
    It calculates the number of injuries per player
    
    Returns:
        Dictionary: Team injuries and injuries for each player

    """
    # Define the path to the injury table JSON file
    injury_path_table = os.path.join(HISTORICAL_DATA_PATH, "injuries_summary.json")

    # Check if the file exists
    if not os.path.exists(injury_path_table):
        raise FileNotFoundError(f"Injury table file not found at path: {injury_path_table}")

    with open(injury_path_table, 'r') as file:
        injury_table = json.load(file)

    total_injuries = 0
    player_injury_data = {}


    # Process the injury table
    for player_id, games in injury_table["players"].items():  # Assuming "players" is the top parent
        player_total = 0
        per_game_injuries = {}

        for game_id, game_data in games.items():
            injuries = game_data.get("injuries", 0)  # Extract the "injuries" key
            player_total += injuries
            per_game_injuries[game_id] = injuries

        player_injury_data[int(player_id)] = {
            "Total Injuries": player_total,
            "Per Game Injuries": per_game_injuries,
        }
        total_injuries += player_total



    return {
        "Total Injuries": total_injuries,
        "Injuries Per Player": player_injury_data,
    }

def calculate_fatigue_levels():
    """
    It calculates the fatigue levels for each player if there is a decreasing distance trend in games.
    

    Returns:
        Dictionary: Fatigue levels for each player and overall totals.
    """
    fatigue_levels = {"Low": 0, "Medium": 0, "High": 0}  # Overall fatigue levels
    player_fatigue_data = {}  # Fatigue levels per player

    for player_folder in os.listdir(HISTORICAL_DATA_PATH):  # Loop through all player folders
        if not player_folder.startswith("gps_"):  # Skip non-GPS folders
            continue

        player_id = int(player_folder.split("_")[1])  # Extract player ID
        distances = []  # List to store total distances per game

        # Loop through game or run the folders for each player
        for run_path in os.listdir(os.path.join(HISTORICAL_DATA_PATH, player_folder)):
            if run_path == '.DS_Store':
                continue
            gps_file_path = os.path.join(HISTORICAL_DATA_PATH, player_folder, run_path, f"{player_folder}.json")
            with open(gps_file_path, 'r') as file:
                data = json.load(file)

            # Calculate total distance for the game
            total_distance = 0
            for i in range(len(data) - 1):
                point1 = data[i]
                point2 = data[i + 1]
                total_distance += haversine_distance(
                    lat1=point1["latitude"],
                    lon1=point1["longitude"],
                    lat2=point2["latitude"],
                    lon2=point2["longitude"],
                )
            distances.append(total_distance)




        # Check for decreasing distance trends across games
        trend_fatigue = 0
        for i in range(1, len(distances)):
            if distances[i] < distances[i - 1]:  # Decreasing trend
                trend_fatigue += 1

        # Determine fatigue level
        if trend_fatigue <= 3:  # Low fatigue
            fatigue_level = "Low"
        elif 4 <= trend_fatigue <= 6:  # Medium fatigue
            fatigue_level = "Medium"
        else:  # High fatigue
            fatigue_level = "High"

        # Update player fatigue data
        player_fatigue_data[player_id] = {
            "Fatigue Level": fatigue_level,
        }


        fatigue_levels[fatigue_level] += 1  # Update overall counts

    return {
        "Fatigue Levels Per Player": player_fatigue_data,
        "Total Fatigue Levels": fatigue_levels,
    }


# Call the main function to calculate team metrics
# team_metrics = calculate_team_metrics()
# print(team_metrics)

# print(team_distance())
# print(team_speeds())
# print(heart_rate_recovery())
# print(calculate_fatigue_levels())
# print(calculate_metrics())