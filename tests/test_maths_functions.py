"""
Unit tests for mathematical functions.
"""
import pytest
from utils.maths_functions import (
    haversine_distance,
    calculate_speed_from_messages,
    calculate_acceleration_from_messages,
    parse_timestamp,
)


class TestHaversineDistance:
    """Tests for haversine_distance function."""
    
    def test_same_point(self):
        """Test distance between same point is zero."""
        distance = haversine_distance(40.0, -75.0, 40.0, -75.0)
        assert distance == 0.0
    
    def test_known_distance(self):
        """Test with known distance (approximately)."""
        # London to Paris is approximately 344 km
        london_lat, london_lon = 51.5074, -0.1278
        paris_lat, paris_lon = 48.8566, 2.3522
        
        distance = haversine_distance(london_lat, london_lon, paris_lat, paris_lon)
        
        # Should be approximately 344 km (344000 meters)
        assert 340000 < distance < 350000
    
    def test_small_distance(self):
        """Test small distance calculation."""
        # Points very close together
        distance = haversine_distance(40.0, -75.0, 40.0001, -75.0001)
        
        # Should be a small positive number
        assert 0 < distance < 50  # Less than 50 meters


class TestParseTimestamp:
    """Tests for parse_timestamp function."""
    
    def test_iso_format_with_microseconds(self):
        """Test parsing ISO format with microseconds."""
        result = parse_timestamp("2024-01-01T12:00:00.123456")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1
        assert result.hour == 12
    
    def test_iso_format_without_microseconds(self):
        """Test parsing ISO format without microseconds."""
        result = parse_timestamp("2024-01-01T12:00:00")
        assert result.year == 2024
        assert result.hour == 12
    
    def test_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            parse_timestamp("not-a-timestamp")


class TestCalculateSpeed:
    """Tests for calculate_speed_from_messages function."""
    
    def test_speed_calculation(self, sample_gps_messages):
        """Test basic speed calculation."""
        messages = sample_gps_messages[:2]
        speed = calculate_speed_from_messages(messages)
        
        # Speed should be positive
        assert speed >= 0
    
    def test_insufficient_messages(self):
        """Test that insufficient messages raises ValueError."""
        with pytest.raises(ValueError):
            calculate_speed_from_messages([{"latitude": 40.0, "longitude": -75.0, "timestamp": "2024-01-01T12:00:00"}])
    
    def test_missing_field(self):
        """Test that missing field raises ValueError."""
        messages = [
            {"latitude": 40.0, "timestamp": "2024-01-01T12:00:00"},  # Missing longitude
            {"latitude": 40.0001, "longitude": -75.0001, "timestamp": "2024-01-01T12:00:01"},
        ]
        with pytest.raises(ValueError):
            calculate_speed_from_messages(messages)


class TestCalculateAcceleration:
    """Tests for calculate_acceleration_from_messages function."""
    
    def test_acceleration_calculation(self, sample_gps_messages):
        """Test basic acceleration calculation."""
        acceleration = calculate_acceleration_from_messages(sample_gps_messages)
        
        # Acceleration can be positive, negative, or zero
        assert isinstance(acceleration, float)
    
    def test_insufficient_messages(self):
        """Test that insufficient messages raises ValueError."""
        messages = [
            {"latitude": 40.0, "longitude": -75.0, "timestamp": "2024-01-01T12:00:00"},
            {"latitude": 40.0001, "longitude": -75.0001, "timestamp": "2024-01-01T12:00:01"},
        ]
        with pytest.raises(ValueError):
            calculate_acceleration_from_messages(messages)
