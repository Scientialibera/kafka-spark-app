"""
Pydantic models for request/response validation.
"""
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegisterDeviceRequest(BaseModel):
    """
    Schema for registering a new device.
    
    Attributes:
        device_name: Unique identifier for the device
        device_schema: Dictionary mapping field names to their data types
    """
    model_config = ConfigDict(
        populate_by_name=True,
        # Serialize using the alias "schema" for backward compatibility
        serialize_by_alias=True,
    )
    
    device_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique device identifier",
        examples=["gps_1", "player_heart_rate_1"]
    )
    device_schema: Dict[str, str] = Field(
        ...,
        alias="schema",
        description="Schema definition mapping field names to types (float, int, string)",
        examples=[{"latitude": "float", "longitude": "float", "timestamp": "string"}]
    )
    
    @field_validator("device_schema")
    @classmethod
    def validate_device_schema(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate that schema is not empty and contains valid types."""
        if not v:
            raise ValueError("Schema cannot be empty")
        
        valid_types = {"float", "int", "string"}
        for field_name, field_type in v.items():
            if field_type not in valid_types:
                raise ValueError(
                    f"Invalid type '{field_type}' for field '{field_name}'. "
                    f"Must be one of: {valid_types}"
                )
        return v
    
    @field_validator("device_name")
    @classmethod
    def validate_device_name(cls, v: str) -> str:
        """Validate device name format."""
        # Remove leading/trailing whitespace
        v = v.strip()
        
        # Check for invalid characters
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Device name can only contain alphanumeric characters, "
                "underscores, and hyphens"
            )
        return v


class DeviceSchemaResponse(BaseModel):
    """Response model for device schema retrieval."""
    model_config = ConfigDict(serialize_by_alias=True, populate_by_name=True)
    
    device_name: str
    device_schema: Dict[str, str] = Field(alias="schema")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class DeviceListResponse(BaseModel):
    """Response model for listing all devices."""
    devices: List[str]


class StreamTriggers(BaseModel):
    """
    Configuration for stream alerting thresholds.
    
    Attributes:
        triggers: Dictionary mapping field names to [min, max] threshold values
    """
    triggers: Dict[str, List[float]] = Field(
        ...,
        description="Dictionary with column names and [min, max] threshold values",
        examples=[{"heart_rate": [70, 140], "temperature": [36.0, 39.0]}]
    )
    window_seconds: int = Field(
        default=5,
        ge=1,
        le=3600,
        description="Window duration in seconds for aggregation"
    )
    table_preappend: Optional[str] = Field(
        default=None,
        description="Optional prefix for the streaming view table name"
    )
    exclude_normal: bool = Field(
        default=False,
        description="Whether to exclude normal values from results"
    )


class KafkaMessage(BaseModel):
    """Model for a single Kafka message."""
    data: Dict[str, Union[str, int, float, bool]]


class TopicMessagesResponse(BaseModel):
    """Response model for topic messages endpoint."""
    device_id: str
    run_id: str
    messages: List[Dict[str, Union[str, int, float, bool]]]


class AggregatedStatsResponse(BaseModel):
    """Response model for aggregated statistics."""
    device_id: str
    aggregation: str
    # Additional fields are dynamic based on schema


class SpeedAccelerationResponse(BaseModel):
    """Response model for speed/acceleration calculation."""
    device_id: str
    run_id: str
    speed: Optional[float] = None
    acceleration: Optional[float] = None


class TeamAverageStatsResponse(BaseModel):
    """Response model for team average statistics."""
    run_id: str
    team_average_speed: Optional[float] = None
    team_average_acceleration: Optional[float] = None
    team_average_heart_rate: Optional[float] = None
    team_average_temperature: Optional[float] = None
