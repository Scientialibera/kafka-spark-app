import json
import os
import datetime
import numpy as np
import math
from datetime import datetime
from fastapi import APIRouter, HTTPException

from backend.config.config import HISTORICAL_DATA_PATH
from utils.maths_functions import haversine_distance

router = APIRouter()

# # Endpoint 1: Team Statistics (Line Chart)
# @router.get("/team-statistics")
# def get_team_statistics():
#     """
#     Endpoint to fetch team statistics (Line Chart Data).
#     """
#         return {
#             "Team Total Distance for all games": metrics["Team Metrics"]["Team Total Distance for All Games"],


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
    Endpoint to fetch total distance per game, recovery metrics, average heart rate recovery, 
    total injuries, and best/worst recommendations for each game.
    """
    try:
        metrics = calculate_metrics()
        return {
            "Team Total Distance Per Game": metrics["Team Metrics"]["Total Distance Per Game"],
            "Team Average Speeds per game": metrics["Team Metrics"]["Team Average Speeds per game"], 
            "Team Max Speeds per Game": metrics["Team Metrics"]["Team Max Speeds per Game"], 
            "Team Total Injuries": metrics["Team Metrics"]["Total Injuries for All Games"],
            "Team Overall max Speed": metrics["Team Metrics"]["Overall Max Team Speed"],
            "Best and Worst Recommendations Per Game": metrics["Best and Worst Recommendations Per Game"],
            "Average Team Distance": metrics["Team Metrics"]["Average Distance for All Games"],
            "Average Team Recovery Rate": metrics["Team Metrics"]["Average Team Recovery Rate"],
            "Player Average Heart Rate Recovery": metrics["Team Metrics"]["Average Heart Rate Recovery for All Players"],
            "Player Average Speeds per Game": metrics["Team Metrics"]["Player Average Speeds per Game"], 
            "Player Average Heart Rate": metrics["Team Metrics"]["Overall Average Heart Rate per Player"],  # New addition
            "Player Max Heart Rate": metrics["Team Metrics"]["Overall Max Heart Rate per Player"],        # New addition
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
    Endpoint to fetch fatigue level distribution across players, per game, and for the entire team.
    """
    try:
        fatigue_data = calculate_fatigue_levels()

        return {
            "Total Fatigue Levels": fatigue_data["Total Fatigue Levels"],        # Aggregated team summary
            "Fatigue Levels Per Game": fatigue_data["Fatigue Levels Per Game"],  # Fatigue summary per game
            "Detailed Fatigue Data": fatigue_data["Fatigue Levels Per Player"]   # Fatigue levels per player per game
        }
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
        return {
            "Best and Worst Recommendations Per Game": metrics["Recommendations"]["Best and Worst"],
            "Player Recommendations Per Game": metrics["Recommendations"]["Player Recommendations"],
            "Aggregated Team Recommendations": metrics["Recommendations"]["Team Recommendations"]  # New addition
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




import random

def calculate_metrics():
    """
    Calculates all required metrics and returns them along with best and worst recommendations per game.
    """
    # Team-related metrics
    team_distance = c_team_distance()
    average_speed, overall_max_speed, player_average_speeds_per_game, team_average_speeds_per_game, team_max_speeds_per_game = team_speeds()
    player_heart_rate_recovery, average_team_recovery_rate, all_players_recovery_details, player_avg_heart_rate, player_max_heart_rate = heart_rate_recovery()
    injury_data = calculate_injuries()
    fatigue_levels = calculate_fatigue_levels()

    # Recommendation templates
    recommendations_templates = {
        "Low Fatigue": [
            "Keep up the good work!",
            "You are performing well, maintain your current routine.",
            "Excellent endurance! Stay consistent with your training."
        ],
        "Medium Fatigue": [
            "Please monitor workload and adjust training intensity if needed.",
            "Consider taking a light day to prevent fatigue buildup.",
            "Balance your workload to avoid overtraining."
        ],
        "High Fatigue": [
            "It's recommended to rest or do lighter training to reduce fatigue.",
            "Take a break and focus on recovery to improve performance.",
            "Prioritize rest and recovery to avoid injury."
        ],
        "High Recovery Rate": [
            "Great recovery rate! Keep up the cardiovascular training.",
            "Your recovery is excellent! Maintain your fitness routine.",
            "Good job on recovery! Continue with endurance exercises."
        ],
        "Low Recovery Rate": [
            "Consider incorporating more aerobic training to improve recovery.",
            "Focus on cardiovascular exercises to enhance your recovery rate.",
            "Your recovery rate is low; try to improve fitness through consistent training."
        ]
    }

    # Compile player metrics for each game
    player_game_metrics = {}
    player_game_recommendations = {}  # To store individual recommendations for each player per game

    for player_id in range(1, 11):
        recovery_data = player_heart_rate_recovery.get(player_id, {}).get("Per Game Recovery Rates", {})
        injuries_data = injury_data["Injuries Per Player"].get(player_id, {}).get("Per Game Injuries", {})
        fatigue_level = fatigue_levels["Fatigue Levels Per Player"].get(player_id, {}).get("Fatigue Level", "Low")

        for game in team_distance["Total Distance Per Game"].keys():
            if game not in player_game_metrics:
                player_game_metrics[game] = []
            if game not in player_game_recommendations:
                player_game_recommendations[game] = {}

            recovery_rate = recovery_data.get(game, 0)
            injuries = injuries_data.get(game, 0)

            player_game_metrics[game].append({
                "Player ID": player_id,
                "Recovery Rate": recovery_rate,
                "Injuries": injuries,
                "Fatigue Level": fatigue_level,
            })

            # Generate individual recommendation for this player in this game
            recommendation = f"Player #{player_id}: "
            if fatigue_level == "High":
                recommendation += random.choice(recommendations_templates["High Fatigue"])
            elif fatigue_level == "Medium":
                recommendation += random.choice(recommendations_templates["Medium Fatigue"])
            else:
                if recovery_rate > 0.5:
                    recommendation += random.choice(recommendations_templates["High Recovery Rate"])
                else:
                    recommendation += random.choice(recommendations_templates["Low Recovery Rate"])

            player_game_recommendations[game][player_id] = recommendation

    # Best and worst recommendations per game
    best_and_worst_recommendations_per_game = {}
    for game, metrics_list in player_game_metrics.items():
        recommendations = []

        for metrics in metrics_list:
            player_id = metrics["Player ID"]
            recommendation = player_game_recommendations[game][player_id]
            recommendations.append((player_id, recommendation, metrics))

        # Sort players based on their metrics: prioritize low fatigue, high recovery, and few injuries
        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: (
                x[2]["Fatigue Level"] == "High",
                -x[2]["Recovery Rate"],
                x[2]["Injuries"]
            )
        )

        best_player = sorted_recommendations[0]
        worst_player = sorted_recommendations[-1]

        best_and_worst_recommendations_per_game[game] = {
            "Best Recommendation": best_player[1],
            "Worst Recommendation": worst_player[1],
        }

        # Aggregate team recommendations based on the most frequent player recommendations per game
        team_recommendations = {}
        for game, player_recs in player_game_recommendations.items():
            # Count the frequency of each recommendation
            rec_count = {}
            for rec in player_recs.values():
                rec_count[rec] = rec_count.get(rec, 0) + 1
            
            # Find the most popular recommendation
            most_popular_recommendation = max(rec_count, key=rec_count.get)
            team_recommendations[game] = most_popular_recommendation


    return {
        "Team Metrics": {
            "Total Distance Per Game": team_distance["Total Distance Per Game"],
            "Team Total Distance for All Games": team_distance["Team Total Distance for All Games"],
            "Average Distance for All Games": team_distance["Average Distance for All Games"],
            "Average Team Recovery Rate": average_team_recovery_rate,
            "Average Heart Rate Recovery for All Players": all_players_recovery_details,
            "Average Player Speed per Game": player_average_speeds_per_game,
            "Average Team Speed per Game": team_average_speeds_per_game,
            "Max Team Speed per Game": team_max_speeds_per_game,
            "Overall Average Speed": average_speed,
            "Overall Max Team Speed": overall_max_speed,
            "Player Average Speeds per Game": player_average_speeds_per_game,
            "Team Average Speeds per game": team_average_speeds_per_game,
            "Team Max Speeds per Game": team_max_speeds_per_game,
            "Overall Average Heart Rate per Player": player_avg_heart_rate,  # New addition
            "Overall Max Heart Rate per Player": player_max_heart_rate,    # New addition

            "Total Injuries for All Games": 
            {
                game: sum(player["Injuries"] for player in metrics_list)
                for game, metrics_list in player_game_metrics.items()
            },

        },
        "Best and Worst Recommendations Per Game": best_and_worst_recommendations_per_game,
        "Recommendations": {
            "Best and Worst": best_and_worst_recommendations_per_game,
            "Player Recommendations": player_game_recommendations,
            "Team Recommendations": team_recommendations  # New addition

        }
    }

def c_team_distance():
    """
    Calculates the total and average distance run per game as well as for all players.
    """
    game_distances = {}

    for player_id in range(1, 11):  # Loop through 10 players
        gps_path = os.path.join(HISTORICAL_DATA_PATH, f"gps_{player_id}")
        if not os.path.exists(gps_path):
            continue  # Skip if the path does not exist

        for run_path in os.listdir(gps_path):  # Loop through all games
            if run_path == '.DS_Store':
                continue
            run_file_path = os.path.join(gps_path, run_path, f"gps_{player_id}.json")
            if not os.path.exists(run_file_path):
                continue

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
    total_distance_all_games = sum(game_distances.values())

    # Calculate average distances per game and overall average
    average_distances_per_game = {
        game: round(distance / 10, 2) for game, distance in game_distances.items()
    }

    average_distance_all_games = round(total_distance_all_games / (total_games * 10), 2) if total_games > 0 else 0

    return {
        "Total Distance Per Game": average_distances_per_game,
        "Team Total Distance for All Games": total_distance_all_games,
        "Average Distance Per Game": average_distances_per_game,
        "Average Distance for All Games": average_distance_all_games,  # This key should be returned correctly
    }

def team_speeds():
    """
    Calculates average speed (km/h) and max team speed, and tracks the max speed for each game.
    Also calculates:
    - Average speeds of players per game
    - Average speeds of the team per game
    - Max speeds of the team per game
    """
    total_speeds = []
    max_speeds_per_game = {}
    player_average_speeds_per_game = {}
    team_average_speeds_per_game = {}
    team_max_speeds_per_game = {}

    for player_id in range(1, 11):  # Loop through 10 players
        speed_path = os.path.join(HISTORICAL_DATA_PATH, f"speed_{player_id}")
        if not os.path.exists(speed_path):
            continue

        for run_path in os.listdir(speed_path):  # Loop through all games
            run_file_path = os.path.join(speed_path, run_path, f"speed_{player_id}.json")
            if not os.path.exists(run_file_path):
                continue

            with open(run_file_path, 'r') as file:
                data = json.load(file)

            # Calculate speeds for the current game
            player_speeds = []
            max_speed = 0

            for entry in data:
                speed_x = entry["speed_x"]
                speed_y = entry["speed_y"]
                speed_z = entry["speed_z"]
                speed_magnitude = math.sqrt(speed_x**2 + speed_y**2 + speed_z**2)
                total_speeds.append(speed_magnitude)
                player_speeds.append(speed_magnitude)
                max_speed = max(max_speed, speed_magnitude)

            # Store player's average speed for the game
            if run_path not in player_average_speeds_per_game:
                player_average_speeds_per_game[run_path] = {}
            player_average_speeds_per_game[run_path][player_id] = round(sum(player_speeds) / len(player_speeds), 2) if player_speeds else 0

            # Track the max speed for the game
            if run_path not in max_speeds_per_game:
                max_speeds_per_game[run_path] = []
            max_speeds_per_game[run_path].append(max_speed)

    # Calculate team average speeds and max speeds per game
    for game, speeds in max_speeds_per_game.items():
        # Calculate the team's average speed for the game
        game_total_speeds = []
        for player_id in range(1, 11):
            if player_id in player_average_speeds_per_game.get(game, {}):
                game_total_speeds.append(player_average_speeds_per_game[game][player_id])

        team_average_speeds_per_game[game] = round(sum(game_total_speeds) / len(game_total_speeds), 2) if game_total_speeds else 0

        # Calculate the max speed among all players for the game
        team_max_speeds_per_game[game] = max(speeds) if speeds else 0

    # Calculate overall average speed and overall max speed
    average_speed = round(sum(total_speeds) / len(total_speeds), 2) if total_speeds else 0
    overall_max_speed = round(max(total_speeds), 2) if total_speeds else 0

    return average_speed, overall_max_speed, player_average_speeds_per_game, team_average_speeds_per_game, team_max_speeds_per_game

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
    Calculates the average heart rate recovery (beats per minute) per player, for each game,
    the detailed heart rate recovery for all players across all games, overall average heart rate,
    and overall maximum heart rate per player.

    Returns:
        Tuple:
            - Player recovery data with per-game recovery rates.
            - Average team recovery rate.
            - Detailed breakdown of heart rate recovery for all players and all games.
            - Overall average heart rate for each player.
            - Overall maximum heart rate for each player.
    """
    player_averages = {}
    total_team_recovery_rate = 0
    team_recovery_count = 0
    all_players_recovery_details = {}  # To store detailed recovery rates for all players
    player_avg_heart_rate = {}         # To store overall average heart rate per player
    player_max_heart_rate = {}         # To store overall maximum heart rate per player

    for player_id in range(1, 11):  # Loop through 10 players
        heart_rate_path = os.path.join(HISTORICAL_DATA_PATH, f"player_heart_rate_{player_id}")

        # Initialize metrics for players
        total_recovery_rate = 0
        total_heart_rate = 0
        max_heart_rate_overall = 0
        total_readings = 0
        run_count = 0
        per_game_recovery_rates = {}

        if not os.path.exists(heart_rate_path):
            continue

        for run_path in os.listdir(heart_rate_path):
            if run_path == '.DS_Store':
                continue
            run_file_path = os.path.join(heart_rate_path, run_path, f"player_heart_rate_{player_id}.json")
            if not os.path.exists(run_file_path):
                continue

            with open(run_file_path, 'r') as file:
                data = json.load(file)

            max_heart_rate = 0
            max_heart_rate_timestamp = None
            heart_rate_drop_60s = None

            for entry in data:
                heart_rate = entry["heart_rate"]
                timestamp = parse_timestamp(entry["timestamp"])

                # Track overall heart rate metrics
                total_heart_rate += heart_rate
                total_readings += 1
                max_heart_rate_overall = max(max_heart_rate_overall, heart_rate)

                if heart_rate > max_heart_rate:
                    max_heart_rate = heart_rate
                    max_heart_rate_timestamp = timestamp

            # Calculate heart rate drop after 60 seconds
            if max_heart_rate_timestamp:
                for entry in data:
                    heart_rate = entry["heart_rate"]
                    timestamp = parse_timestamp(entry["timestamp"])
                    time_diff = (timestamp - max_heart_rate_timestamp).total_seconds()

                    if 1 <= time_diff <= 60:
                        heart_rate_drop_60s = max_heart_rate - heart_rate

            if heart_rate_drop_60s is not None:
                recovery_rate = round(heart_rate_drop_60s / 60, 2)
                total_recovery_rate += recovery_rate
                team_recovery_count += 1
                total_team_recovery_rate += recovery_rate

                # Store per-game recovery rate
                per_game_recovery_rates[run_path] = recovery_rate

                # Store detailed recovery rate for all players
                if player_id not in all_players_recovery_details:
                    all_players_recovery_details[player_id] = {}
                all_players_recovery_details[player_id][run_path] = recovery_rate

                run_count += 1

        # Calculate average recovery rate for this player
        if run_count > 0:
            player_averages[player_id] = {
                "Average Recovery Rate (BPM/Sec)": round(total_recovery_rate / run_count, 2),
                "Per Game Recovery Rates": per_game_recovery_rates,
            }

        # Store overall average heart rate and max heart rate for each player
        player_avg_heart_rate[player_id] = round(total_heart_rate / total_readings, 2) if total_readings > 0 else 0
        player_max_heart_rate[player_id] = max_heart_rate_overall

    # Calculate average team recovery rate
    average_team_recovery_rate = round(total_team_recovery_rate / team_recovery_count, 2) if team_recovery_count > 0 else None

    return player_averages, average_team_recovery_rate, all_players_recovery_details, player_avg_heart_rate, player_max_heart_rate


def calculate_injuries():
    """
    It calculates the number of injuries per player and per game.
    
    Returns:
        Dictionary: Contains total injuries for all games and injuries per player.
    """
    # Define the path to the injury table JSON file
    injury_path_table = os.path.join(HISTORICAL_DATA_PATH, "injuries_summary.json")

    # Check if the file exists
    if not os.path.exists(injury_path_table):
        raise FileNotFoundError(f"Injury table file not found at path: {injury_path_table}")

    try:
        with open(injury_path_table, 'r') as file:
            injury_table = json.load(file)
        
        total_injuries = 0
        player_injury_data = {}
        total_injuries_per_game = {}

        # Process the injury table
        for player_id, runs in injury_table["players"].items():
            player_total = 0
            per_game_injuries = {}

            for run_id, run_data in runs.items():
                injury_count = run_data.get("injuries", 0)
                player_total += injury_count
                per_game_injuries[run_id] = injury_count

                # Accumulate total injuries per game across all players
                if run_id not in total_injuries_per_game:
                    total_injuries_per_game[run_id] = 0
                total_injuries_per_game[run_id] += injury_count

            player_injury_data[int(player_id)] = {
                "Total Injuries": player_total,
                "Per Game Injuries": per_game_injuries,
            }
            total_injuries += player_total

        return {
            "Total Injuries": total_injuries,
            "Injuries Per Player": player_injury_data,
            "Total Injuries Per Game": total_injuries_per_game,  # Added this key for per-game injuries
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing injuries data: {str(e)}")


def calculate_fatigue_levels():
    """
    Calculates the fatigue levels for each player based on percentage changes, consecutive declines, and variability in distances.

    Returns:
        Dictionary: 
            - Fatigue levels for each player across all games.
            - Aggregated fatigue levels as a string for the whole team.
            - Fatigue levels aggregated for each game.
    """
    fatigue_levels = {"Low": 0, "Medium": 0, "High": 0}  # Overall fatigue levels
    player_fatigue_data = {}  # Fatigue levels per player
    game_fatigue_data = {}  # Fatigue levels aggregated per game

    for player_folder in os.listdir(HISTORICAL_DATA_PATH):  # Loop through all player folders
        if not player_folder.startswith("gps_"):  # Skip non-GPS folders
            continue

        player_id = int(player_folder.split("_")[1])  # Extract player ID
        player_fatigue_data[player_id] = {}  # Store fatigue levels per game for the player
        distances = []  # List to store total distances per game

        # Loop through game or run folders for each player
        for run_path in sorted(os.listdir(os.path.join(HISTORICAL_DATA_PATH, player_folder))):
            if run_path == '.DS_Store':
                continue
            gps_file_path = os.path.join(HISTORICAL_DATA_PATH, player_folder, run_path, f"{player_folder}.json")

            if not os.path.exists(gps_file_path):
                continue

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

            # Calculate fatigue level for this game
            fatigue_level = determine_fatigue_level(distances)
            player_fatigue_data[player_id][run_path] = fatigue_level

            # Aggregate fatigue levels per game
            if run_path not in game_fatigue_data:
                game_fatigue_data[run_path] = {"Low": 0, "Medium": 0, "High": 0}
            game_fatigue_data[run_path][fatigue_level] += 1

            # Update overall counts
            fatigue_levels[fatigue_level] += 1

    # Convert overall fatigue levels to a string summary
    team_fatigue_summary = f"Low: {fatigue_levels['Low']}, Medium: {fatigue_levels['Medium']}, High: {fatigue_levels['High']}"

    # Convert game fatigue levels to string summaries
    game_fatigue_summary = {
        game: f"Low: {counts['Low']}, Medium: {counts['Medium']}, High: {counts['High']}"
        for game, counts in game_fatigue_data.items()
    }

    return {
        "Fatigue Levels Per Player": player_fatigue_data,
        "Total Fatigue Levels": team_fatigue_summary,
        "Fatigue Levels Per Game": game_fatigue_summary,
    }


def determine_fatigue_level(distances):
    """
    Helper function to determine the fatigue level based on distances.
    """
    # Calculate percentage changes
    percentage_changes = []
    consecutive_declines = 0
    max_consecutive_declines = 0

    for i in range(1, len(distances)):
        if distances[i - 1] != 0:
            change = ((distances[i] - distances[i - 1]) / distances[i - 1]) * 100
            percentage_changes.append(change)

            # Track consecutive declines
            if change < 0:
                consecutive_declines += 1
            else:
                max_consecutive_declines = max(max_consecutive_declines, consecutive_declines)
                consecutive_declines = 0

    max_consecutive_declines = max(max_consecutive_declines, consecutive_declines)

    # Calculate standard deviation of distances
    std_dev = np.std(distances) if len(distances) > 1 else 0
    avg_percentage_change = sum(percentage_changes) / len(percentage_changes) if percentage_changes else 0

    # Determine fatigue level based on multiple factors
    if avg_percentage_change >= -5 and max_consecutive_declines <= 2 and std_dev < 1000:
        return "Low"
    elif -15 < avg_percentage_change < -5 or (2 < max_consecutive_declines <= 4) or (1000 <= std_dev < 2000):
        return "Medium"
    else:
        return "High"
