"""
Mathematical functions for sports analytics calculations.

This module provides functions for calculating speed, acceleration,
and distance using GPS coordinates and timestamps.
"""
import math
from datetime import datetime
from typing import Dict, List, Union

# Earth's radius in meters (WGS84 mean radius)
EARTH_RADIUS_METERS = 6371000


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points on Earth.
    
    Uses the Haversine formula to compute the shortest distance over
    the Earth's surface between two points specified by latitude and longitude.
    
    Args:
        lat1: Latitude of the first point in degrees
        lon1: Longitude of the first point in degrees
        lat2: Latitude of the second point in degrees
        lon2: Longitude of the second point in degrees
        
    Returns:
        Distance between the points in meters
    """
    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_phi / 2) ** 2 +
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_METERS * c


def parse_timestamp(timestamp: Union[str, datetime]) -> datetime:
    """
    Parse a timestamp string into a datetime object.
    
    Handles both ISO format with and without microseconds.
    
    Args:
        timestamp: Timestamp string or datetime object
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If timestamp format is not recognized
    """
    if isinstance(timestamp, datetime):
        return timestamp
        
    # Try parsing with microseconds first
    try:
        return datetime.fromisoformat(timestamp)
    except ValueError:
        pass
    
    # Try common formats
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse timestamp: {timestamp}")


def calculate_speed_from_points(
    lat1: float,
    lon1: float,
    time1: Union[str, datetime],
    lat2: float,
    lon2: float,
    time2: Union[str, datetime]
) -> float:
    """
    Calculate speed between two GPS points.
    
    Args:
        lat1, lon1: Coordinates of the first point
        time1: Timestamp of the first point
        lat2, lon2: Coordinates of the second point
        time2: Timestamp of the second point
        
    Returns:
        Speed in meters per second
        
    Raises:
        ValueError: If time difference is zero
    """
    # Parse timestamps if needed
    if isinstance(time1, str):
        time1 = parse_timestamp(time1)
    if isinstance(time2, str):
        time2 = parse_timestamp(time2)
    
    time_diff = (time2 - time1).total_seconds()
    
    if time_diff == 0:
        raise ValueError("Time difference between points is zero")
    
    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance / abs(time_diff)


def calculate_speed_from_messages(messages: List[Dict]) -> float:
    """
    Calculate instantaneous speed from the last two GPS messages.
    
    Args:
        messages: List of at least 2 GPS messages with latitude,
                 longitude, and timestamp fields
        
    Returns:
        Speed in meters per second
        
    Raises:
        ValueError: If insufficient messages or invalid data
    """
    if len(messages) < 2:
        raise ValueError("At least 2 messages are required to calculate speed")
    
    try:
        point1, point2 = messages[0], messages[1]
        
        return calculate_speed_from_points(
            lat1=point1["latitude"],
            lon1=point1["longitude"],
            time1=point1["timestamp"],
            lat2=point2["latitude"],
            lon2=point2["longitude"],
            time2=point2["timestamp"]
        )
    except KeyError as e:
        raise ValueError(f"Missing required field in message: {e}")
    except Exception as e:
        raise ValueError(f"Error calculating speed: {e}")


def calculate_acceleration_from_messages(messages: List[Dict]) -> float:
    """
    Calculate acceleration from the last three GPS messages.
    
    Computes the change in speed over time between consecutive points.
    
    Args:
        messages: List of at least 3 GPS messages with latitude,
                 longitude, and timestamp fields
        
    Returns:
        Acceleration in meters per second squared
        
    Raises:
        ValueError: If insufficient messages or invalid data
    """
    if len(messages) < 3:
        raise ValueError("At least 3 messages are required to calculate acceleration")
    
    try:
        point1, point2, point3 = messages[0], messages[1], messages[2]
        
        # Parse timestamps
        time1 = parse_timestamp(point1["timestamp"])
        time2 = parse_timestamp(point2["timestamp"])
        time3 = parse_timestamp(point3["timestamp"])
        
        # Calculate speeds at two intervals
        speed1 = calculate_speed_from_points(
            point1["latitude"], point1["longitude"], time1,
            point2["latitude"], point2["longitude"], time2
        )
        speed2 = calculate_speed_from_points(
            point2["latitude"], point2["longitude"], time2,
            point3["latitude"], point3["longitude"], time3
        )
        
        # Calculate time difference for acceleration
        time_diff = (time3 - time1).total_seconds()
        
        if time_diff == 0:
            raise ValueError("Time difference between points is zero")
        
        return (speed2 - speed1) / time_diff
        
    except KeyError as e:
        raise ValueError(f"Missing required field in message: {e}")
    except Exception as e:
        raise ValueError(f"Error calculating acceleration: {e}")