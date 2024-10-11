from pydantic import BaseModel
from typing import Dict

# Schema for registering a device
class RegisterDeviceRequest(BaseModel):
    device_name: str
    schema: Dict