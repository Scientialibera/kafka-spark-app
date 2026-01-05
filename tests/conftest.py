"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_device_schema():
    """Sample device schema for testing."""
    return {
        "device_name": "test_gps_1",
        "schema": {
            "latitude": "float",
            "longitude": "float",
            "timestamp": "string"
        }
    }


@pytest.fixture
def sample_heart_rate_schema():
    """Sample heart rate device schema for testing."""
    return {
        "device_name": "test_heart_rate_1",
        "schema": {
            "heart_rate": "int",
            "timestamp": "string"
        }
    }


@pytest.fixture
def sample_gps_messages():
    """Sample GPS messages for speed/acceleration testing."""
    return [
        {"latitude": 40.0001, "longitude": -75.0001, "timestamp": "2024-01-01T12:00:00"},
        {"latitude": 40.0002, "longitude": -75.0002, "timestamp": "2024-01-01T12:00:01"},
        {"latitude": 40.0004, "longitude": -75.0004, "timestamp": "2024-01-01T12:00:02"},
    ]
