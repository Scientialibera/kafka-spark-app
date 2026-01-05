"""
Constants and configuration values for the Sports Prophet application.
"""
from typing import Dict, List, Tuple

# =============================================================================
# API Endpoints
# =============================================================================

# Device Registration Endpoints
REGISTER_DEVICE_ENDPOINT: str = "/register-device"
UPDATE_DEVICE_ENDPOINT: str = "/update-device"
DELETE_DEVICE_ENDPOINT: str = "/delete-device/{device_id}"
ALL_DEVICES_ENDPOINT: str = "/devices"
GET_DEVICE_ENDPOINT: str = "/device/{device_id}"

# Streaming Endpoints
WEBSOCKET_STREAM_ENDPOINT: str = "/send-stream/{device_id}/{run_id}"
START_STREAM_ENDPOINT: str = "/start-stream/{device_id}/{run_id}"
END_STREAM_ENDPOINT: str = "/stop-stream/{device_id}/{run_id}"

# Stats Endpoints
GET_STATS_ENDPOINT: str = "/get-stats/{device_id}/{run_id}"
GET_SPEED_ENDPOINT: str = "/get-speed/{device_id}/{run_id}"
ALARM_ENDPOINT: str = "/get-notification/{device_id}/{run_id}"
AVERAGE_STATS_ENDPOINT: str = "/get-team-average-stats/{num_players}/{run_id}"

# Kafka Topic Endpoints
GET_TOPIC_MESSAGES_ENDPOINT: str = "/get-topic-messages/{device_id}/{run_id}"
GET_AVERAGE_TOPIC_MESSAGES_ENDPOINT: str = "/get-team-kafka-stats/{num_players}/{run_id}"
DELETE_TOPIC_ENDPOINT: str = "/delete-topic/{device_id}/{run_id}"
DELETE_ALL_TOPICS_ENDPOINT: str = "/delete-all-topics"
LIST_TOPICS_ENDPOINT: str = "/list-topics"

# Synthetic Data Endpoint
START_SYNTHETIC_DATA_ENDPOINT: str = "/start-synthetic-data"

# =============================================================================
# Data Simulation Constants
# =============================================================================

# GPS boundaries (pitch coordinates)
GPS_CONFIG: Dict[str, float] = {
    "PITCH_LAT_MIN": 40.0,
    "PITCH_LAT_MAX": 40.0009,
    "PITCH_LON_MIN": -75.0012,
    "PITCH_LON_MAX": -75.0,
    "STEP_SIZE_LAT": 0.00001,
    "STEP_SIZE_LON": 0.000015,
}

# Heart rate boundaries
HEART_RATE_CONFIG: Dict[str, Tuple[int, int]] = {
    "NORMAL_RANGE": (70, 140),
    "OUT_OF_BOUNDS_LOW": (30, 60),
    "OUT_OF_BOUNDS_HIGH": (160, 200),
}

# Temperature boundaries
TEMPERATURE_CONFIG: Dict[str, Tuple[float, float]] = {
    "NORMAL_RANGE": (36.0, 39.0),
    "OUT_OF_BOUNDS_LOW": (34.0, 35.5),
    "OUT_OF_BOUNDS_HIGH": (39.5, 42.0),
}

# Streaming timing
STREAMING_CONFIG: Dict[str, float] = {
    "INTERVAL_SECONDS": 0.5,
    "OUT_OF_BOUNDS_INTERVAL": 100,
    "DEFAULT_WINDOW_SECONDS": 5,
    "KAFKA_TIMEOUT_SECONDS": 5,
}

# =============================================================================
# Recommendation Templates
# =============================================================================

RECOMMENDATION_TEMPLATES: Dict[str, List[str]] = {
    "Low Fatigue": [
        "Keep up the good work!",
        "You are performing well, maintain your current routine.",
        "Excellent endurance! Stay consistent with your training."
    ],
    "Medium Fatigue": [
        "Monitor the workload and adjust training intensity if needed.",
        "Consider taking a light day to prevent fatigue buildup.",
        "Balance your workload to avoid overtraining."
    ],
    "High Fatigue": [
        "Recommended to rest or do lighter training to reduce fatigue.",
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
        "Your recovery rate is low; improve fitness through consistent training."
    ]
}

# =============================================================================
# Supported Data Types
# =============================================================================

SUPPORTED_DATA_TYPES: Dict[str, type] = {
    "float": float,
    "int": int,
    "string": str,
}

# =============================================================================
# Default Values
# =============================================================================

DEFAULT_NUM_PLAYERS: int = 10
DEFAULT_AGGREGATION_TYPE: str = "average"
AGGREGATION_TYPES: List[str] = ["average", "max", "min", "sum"]
