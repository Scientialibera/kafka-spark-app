"""
Unit tests for file management utilities.
"""
import pytest
from utils.file_management import (
    kafka_topic_name,
    validate_data,
)


class TestKafkaTopicName:
    """Tests for kafka_topic_name function."""
    
    def test_basic_topic_name(self):
        """Test basic topic name generation."""
        result = kafka_topic_name("gps_1", "run_001")
        assert result == "gps_1_run_001"
    
    def test_empty_strings(self):
        """Test with empty strings."""
        result = kafka_topic_name("", "")
        assert result == "_"
    
    def test_special_characters(self):
        """Test with special characters in IDs."""
        result = kafka_topic_name("device-1", "run-001")
        assert result == "device-1_run-001"


class TestValidateData:
    """Tests for validate_data function."""
    
    def test_valid_data(self):
        """Test validation with valid data."""
        data = {"latitude": 40.0, "longitude": -75.0, "timestamp": "2024-01-01"}
        schema = {"latitude": "float", "longitude": "float", "timestamp": "string"}
        assert validate_data(data, schema) is True
    
    def test_int_for_float(self):
        """Test that int is accepted for float type."""
        data = {"value": 42, "timestamp": "2024-01-01"}
        schema = {"value": "float", "timestamp": "string"}
        assert validate_data(data, schema) is True
    
    def test_missing_key(self):
        """Test validation fails with missing key."""
        data = {"latitude": 40.0}
        schema = {"latitude": "float", "longitude": "float"}
        assert validate_data(data, schema) is False
    
    def test_extra_key(self):
        """Test validation fails with extra key."""
        data = {"latitude": 40.0, "longitude": -75.0, "extra": "value"}
        schema = {"latitude": "float", "longitude": "float"}
        assert validate_data(data, schema) is False
    
    def test_wrong_type_string_for_int(self):
        """Test validation fails with wrong type."""
        data = {"heart_rate": "not_an_int"}
        schema = {"heart_rate": "int"}
        assert validate_data(data, schema) is False
    
    def test_wrong_type_string_for_float(self):
        """Test validation fails with string for float."""
        data = {"latitude": "not_a_float"}
        schema = {"latitude": "float"}
        assert validate_data(data, schema) is False
