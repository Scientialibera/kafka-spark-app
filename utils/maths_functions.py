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
