#!/usr/bin/env python3
"""
Synthetic data producer for Sports Prophet.

Streams GPS, heart rate, and temperature data via WebSocket to simulate
live sensor feeds from multiple players.

Usage:
    python scripts/produce_data.py [--base-url URL] [--num-players N] [--duration S] [--run-id ID]
"""
import argparse
import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone

import websockets

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Football pitch boundaries (latitude/longitude)
PITCH_LAT_MIN = 40.0
PITCH_LAT_MAX = 40.0009
PITCH_LON_MIN = -75.0012
PITCH_LON_MAX = -75.0
STEP_SIZE_LAT = 0.00001
STEP_SIZE_LON = 0.000015

HR_NORMAL = (70, 140)
HR_OUT_LOW = (30, 60)
HR_OUT_HIGH = (160, 200)

TEMP_NORMAL = (36.0, 39.0)
TEMP_OUT_LOW = (34.0, 35.5)
TEMP_OUT_HIGH = (39.5, 42.0)

OUT_OF_BOUNDS_INTERVAL = 100
SEND_INTERVAL = 0.5


def random_walk(lat: float, lon: float) -> tuple[float, float]:
    lat = max(min(lat + random.uniform(-STEP_SIZE_LAT, STEP_SIZE_LAT), PITCH_LAT_MAX), PITCH_LAT_MIN)
    lon = max(min(lon + random.uniform(-STEP_SIZE_LON, STEP_SIZE_LON), PITCH_LON_MAX), PITCH_LON_MIN)
    return lat, lon


def generate_gps(lat: float, lon: float, count: int) -> tuple[dict, float, float]:
    if count > 0 and count % OUT_OF_BOUNDS_INTERVAL == 0:
        lat = PITCH_LAT_MAX + random.uniform(0.0001, 0.0005)
        lon = PITCH_LON_MAX + random.uniform(0.0001, 0.0005)
    else:
        lat, lon = random_walk(lat, lon)
    return {
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }, lat, lon


def generate_heart_rate(count: int) -> dict:
    if count > 0 and count % OUT_OF_BOUNDS_INTERVAL == 0:
        hr = random.choice([random.randint(*HR_OUT_LOW), random.randint(*HR_OUT_HIGH)])
    else:
        hr = random.randint(*HR_NORMAL)
    return {"heart_rate": hr, "timestamp": datetime.now(timezone.utc).isoformat()}


def generate_temperature(count: int) -> dict:
    if count > 0 and count % OUT_OF_BOUNDS_INTERVAL == 0:
        temp = random.choice([
            round(random.uniform(*TEMP_OUT_LOW), 1),
            round(random.uniform(*TEMP_OUT_HIGH), 1),
        ])
    else:
        temp = round(random.uniform(*TEMP_NORMAL), 1)
    return {"temperature": temp, "timestamp": datetime.now(timezone.utc).isoformat()}


async def stream_device(ws_url: str, device_id: str, run_id: str, schema_type: str, duration: float) -> None:
    endpoint = f"{ws_url}/send-stream/{device_id}/{run_id}"
    try:
        async with websockets.connect(endpoint) as ws:
            end_time = time.time() + duration
            lat = (PITCH_LAT_MIN + PITCH_LAT_MAX) / 2
            lon = (PITCH_LON_MIN + PITCH_LON_MAX) / 2
            count = 0

            while time.time() < end_time:
                if schema_type == "gps":
                    data, lat, lon = generate_gps(lat, lon, count)
                elif schema_type == "heart_rate":
                    data = generate_heart_rate(count)
                elif schema_type == "temperature":
                    data = generate_temperature(count)
                else:
                    raise ValueError(f"Unknown schema type: {schema_type}")

                await ws.send(json.dumps(data))
                count += 1
                if count % 100 == 0:
                    log.info("%s sent %d messages", device_id, count)
                await asyncio.sleep(SEND_INTERVAL)

            log.info("%s finished: %d messages sent", device_id, count)
    except Exception as exc:
        log.error("Error streaming %s: %s", device_id, exc)


async def run(ws_url: str, num_players: int, duration: float, run_id: str) -> None:
    tasks = [
        *[stream_device(ws_url, f"gps_{i}", run_id, "gps", duration) for i in range(1, num_players + 1)],
        *[stream_device(ws_url, f"player_heart_rate_{i}", run_id, "heart_rate", duration) for i in range(1, num_players + 1)],
        *[stream_device(ws_url, f"player_temperature_{i}", run_id, "temperature", duration) for i in range(1, num_players + 1)],
    ]
    log.info("Starting %d producers for %ds (run: %s)", len(tasks), duration, run_id)
    await asyncio.gather(*tasks)
    log.info("All producers finished")


def main() -> None:
    parser = argparse.ArgumentParser(description="Stream synthetic sensor data")
    parser.add_argument("--ws-url", default="ws://localhost:8000", help="WebSocket base URL")
    parser.add_argument("--num-players", type=int, default=10, help="Number of players")
    parser.add_argument("--duration", type=int, default=120, help="Duration in seconds")
    parser.add_argument("--run-id", default="run_001", help="Run ID")
    args = parser.parse_args()

    asyncio.run(run(args.ws_url, args.num_players, args.duration, args.run_id))


if __name__ == "__main__":
    main()
