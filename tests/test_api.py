"""
Unit tests for API endpoints.
"""
import pytest


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_returns_message(self, client):
        """Test that root endpoint returns expected message."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestDeviceRegistration:
    """Tests for device registration endpoints."""
    
    def test_register_device_success(self, client, sample_device_schema):
        """Test successful device registration."""
        response = client.post("/register-device", json=sample_device_schema)
        # Either 200 (success) or 400 (already exists)
        assert response.status_code in [200, 400]
    
    def test_register_device_empty_schema(self, client):
        """Test registration with empty schema fails."""
        payload = {
            "device_name": "test_device",
            "schema": {}
        }
        response = client.post("/register-device", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_register_device_invalid_type(self, client):
        """Test registration with invalid type fails."""
        payload = {
            "device_name": "test_device",
            "schema": {"field": "invalid_type"}
        }
        response = client.post("/register-device", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_get_all_devices(self, client):
        """Test getting list of all devices."""
        response = client.get("/devices")
        assert response.status_code == 200
        assert "devices" in response.json()
        assert isinstance(response.json()["devices"], list)
