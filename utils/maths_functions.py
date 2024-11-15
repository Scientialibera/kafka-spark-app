from datetime import datetime
import math

def calculate_speed_from_messages(messages):
    """
    Calculate the speed using the last two messages containing GPS coordinates.

    Args:
        messages (List[Dict]): The last two Kafka messages containing 'latitude', 'longitude', and 'timestamp'.

    Returns:
        float: The calculated speed in meters per second.
    """
    try:
        # Ensure messages are sorted correctly (the latest should be the second message)
        point1, point2 = messages[0], messages[1]
        lat1, lon1, time1 = point1["latitude"], point1["longitude"], point1["timestamp"]
        lat2, lon2, time2 = point2["latitude"], point2["longitude"], point2["timestamp"]

        # Convert timestamps to datetime objects
        time1 = datetime.fromisoformat(time1)
        time2 = datetime.fromisoformat(time2)

        # Calculate the time difference in seconds
        time_diff = (time2 - time1).total_seconds()

        # If time difference is zero, avoid division by zero
        if time_diff == 0:
            raise ValueError("Time difference between the two points is zero.")

        # Calculate the distance using the Haversine formula
        distance = haversine_distance(lat1, lon1, lat2, lon2)

        # Calculate the speed (distance/time)
        speed = distance / time_diff

        return speed

    except Exception as e:
        raise ValueError(f"Error calculating speed: {str(e)}")


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface given their latitude and longitude.
    Returns the distance in meters.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.
    
    Returns:
        float: The calculated distance in meters.
    """
    R = 6371000  # Radius of Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def calculate_acceleration_from_messages(messages):
    """
    Calculate acceleration using the last three messages containing GPS coordinates and timestamps.

    Args:
        messages (List[Dict]): The last three Kafka messages containing 'latitude', 'longitude', and 'timestamp'.

    Returns:
        float: The calculated acceleration in meters per second squared.
    """
    try:
        # Ensure messages are sorted correctly
        point1, point2, point3 = messages[0], messages[1], messages[2]
        
        # Extract latitudes, longitudes, and timestamps
        lat1, lon1, time1 = point1["latitude"], point1["longitude"], point1["timestamp"]
        lat2, lon2, time2 = point2["latitude"], point2["longitude"], point2["timestamp"]
        lat3, lon3, time3 = point3["latitude"], point3["longitude"], point3["timestamp"]

        # Convert timestamps to datetime objects
        time1, time2, time3 = datetime.fromisoformat(time1), datetime.fromisoformat(time2), datetime.fromisoformat(time3)

        # Calculate speeds at two intervals
        speed1 = calculate_speed_from_points(lat1, lon1, time1, lat2, lon2, time2)
        speed2 = calculate_speed_from_points(lat2, lon2, time2, lat3, lon3, time3)

        # Calculate time difference between the two intervals
        time_diff = (time3 - time1).total_seconds()

        if time_diff == 0:
            raise ValueError("Time difference between the points is zero.")

        # Calculate acceleration (change in speed over time)
        acceleration = (speed2 - speed1) / time_diff

        return acceleration

    except Exception as e:
        raise ValueError(f"Error calculating acceleration: {str(e)}")


def calculate_speed_from_points(lat1, lon1, time1, lat2, lon2, time2):
    """
    Helper function to calculate speed between two points.

    Args:
        lat1, lon1 (float): Latitude and longitude of the first point.
        time1 (datetime): Timestamp of the first point.
        lat2, lon2 (float): Latitude and longitude of the second point.
        time2 (datetime): Timestamp of the second point.

    Returns:
        float: The speed between the two points in meters per second.
    """
    time_diff = (time2 - time1).total_seconds()
    if time_diff == 0:
        raise ValueError("Time difference between the two points is zero.")

    distance = haversine_distance(lat1, lon1, lat2, lon2)
    speed = distance / time_diff

    return speed