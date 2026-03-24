#!/usr/bin/env python3
"""
Register device schemas with the Sports Prophet API.

Registers GPS, accelerometer, wind, temperature, and heart rate devices
so the API knows how to validate incoming sensor data.

Usage:
    python scripts/register_devices.py [--base-url URL] [--num-devices N]
"""
import argparse
import logging
import sys

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DEVICE_SCHEMAS = {
    "gps": {
        "latitude": "float",
        "longitude": "float",
        "timestamp": "string",
    },
    "accel": {
        "acceleration_x": "float",
        "acceleration_y": "float",
        "acceleration_z": "float",
        "timestamp": "string",
    },
    "wind": {
        "speed": "float",
        "direction": "float",
        "timestamp": "string",
    },
    "player_temperature": {
        "temperature": "float",
        "timestamp": "string",
    },
    "player_heart_rate": {
        "heart_rate": "int",
        "timestamp": "string",
    },
}


def register_devices(base_url: str, num_devices: int) -> None:
    url = f"{base_url}/register-device"
    success = 0
    errors = 0

    for device_type, schema in DEVICE_SCHEMAS.items():
        for i in range(1, num_devices + 1):
            device_name = f"{device_type}_{i}"
            payload = {"device_name": device_name, "schema": schema}

            try:
                resp = requests.post(url, json=payload, timeout=10)
                if resp.status_code == 200:
                    log.info("Registered %s: %s", device_name, resp.json().get("message"))
                    success += 1
                else:
                    log.warning("Failed %s: %s %s", device_name, resp.status_code, resp.text)
                    errors += 1
            except requests.RequestException as exc:
                log.error("Error registering %s: %s", device_name, exc)
                errors += 1

    log.info("Done: %d registered, %d errors", success, errors)


def main() -> None:
    parser = argparse.ArgumentParser(description="Register device schemas")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--num-devices", type=int, default=10, help="Devices per type")
    args = parser.parse_args()

    register_devices(args.base_url, args.num_devices)


if __name__ == "__main__":
    main()
