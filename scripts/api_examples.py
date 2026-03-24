#!/usr/bin/env python3
"""
API client examples for Sports Prophet.

Demonstrates how to call the main API endpoints: start synthetic streams,
fetch team statistics, analyze heart rate, and retrieve GPS locations.

Usage:
    python scripts/api_examples.py [--base-url URL] [--num-players N] [--run-id ID]
    python scripts/api_examples.py --action start-stream
    python scripts/api_examples.py --action team-speed
    python scripts/api_examples.py --action team-vitals
    python scripts/api_examples.py --action heart-rate
    python scripts/api_examples.py --action gps
    python scripts/api_examples.py --action all
"""
import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def start_synthetic_stream(base_url: str, num_players: int, stream_seconds: int) -> None:
    """Start synthetic data stream via the API."""
    log.info("Starting synthetic stream: %d players, %ds", num_players, stream_seconds)
    resp = requests.post(
        f"{base_url}/start-synthetic-data",
        params={"num_players": num_players, "stream_seconds": stream_seconds},
        timeout=15,
    )
    if resp.ok:
        log.info("Response: %s", resp.json())
    else:
        log.error("Error %d: %s", resp.status_code, resp.text)


def get_team_speed(base_url: str, num_players: int, run_id: str) -> None:
    """Get team average speed and acceleration."""
    url = f"{base_url}/get-team-average-stats/{num_players}/{run_id}"
    resp = requests.get(url, timeout=30)
    if resp.ok:
        data = resp.json()
        log.info("Team speed: %.4f, acceleration: %.4f",
                 data.get("team_average_speed", 0), data.get("team_average_acceleration", 0))
    else:
        log.error("Error %d: %s", resp.status_code, resp.text)


def get_team_vitals(base_url: str, num_players: int, run_id: str) -> None:
    """Get team average heart rate and temperature from Kafka."""
    url = f"{base_url}/get-team-kafka-stats/{num_players}/{run_id}"
    resp = requests.get(url, timeout=30)
    if resp.ok:
        data = resp.json()
        log.info("Heart rate: %.1f, temperature: %.2f",
                 data.get("team_average_heart_rate", 0), data.get("team_average_temperature", 0))
    else:
        log.error("Error %d: %s", resp.status_code, resp.text)


def analyze_heart_rate(base_url: str, num_players: int, run_id: str) -> None:
    """Analyze heart rate and classify as low/normal/high."""
    url = f"{base_url}/analyze-heart-rate/{num_players}/{run_id}"
    resp = requests.get(url, timeout=30)
    if resp.ok:
        data = resp.json()
        for entry in data.get("analyzed_data", []):
            if "error" in entry:
                log.warning("%s: %s", entry.get("device_id"), entry["error"])
            else:
                log.info("%s: HR=%s, alarm=%s",
                         entry.get("device_id"), entry.get("heart_rate"), entry.get("alarm_type"))
    else:
        log.error("Error %d: %s", resp.status_code, resp.text)


def get_gps_locations(base_url: str, num_players: int, run_id: str) -> None:
    """Fetch latest GPS location for each player concurrently."""
    device_ids = [f"gps_{i}" for i in range(1, num_players + 1)]

    def fetch_one(device_id: str) -> dict | None:
        url = f"{base_url}/get-topic-messages/{device_id}/{run_id}?limit=1"
        try:
            resp = requests.get(url, timeout=10)
            return resp.json() if resp.ok else None
        except requests.RequestException as exc:
            log.error("Error fetching %s: %s", device_id, exc)
            return None

    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(fetch_one, d): d for d in device_ids}
        for future in as_completed(futures):
            result = future.result()
            if result and result.get("messages"):
                msg = result["messages"][0]
                log.info("%s: lat=%.6f, lon=%.6f",
                         result["device_id"], msg.get("latitude", 0), msg.get("longitude", 0))
            else:
                log.warning("%s: no data", futures[future])


ACTIONS = {
    "start-stream": lambda args: start_synthetic_stream(args.base_url, args.num_players, args.stream_seconds),
    "team-speed": lambda args: get_team_speed(args.base_url, args.num_players, args.run_id),
    "team-vitals": lambda args: get_team_vitals(args.base_url, args.num_players, args.run_id),
    "heart-rate": lambda args: analyze_heart_rate(args.base_url, args.num_players, args.run_id),
    "gps": lambda args: get_gps_locations(args.base_url, args.num_players, args.run_id),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sports Prophet API examples")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--num-players", type=int, default=3, help="Number of players")
    parser.add_argument("--run-id", default="run_001", help="Run ID")
    parser.add_argument("--stream-seconds", type=int, default=50, help="Seconds for synthetic stream")
    parser.add_argument("--action", default="all", choices=[*ACTIONS.keys(), "all"],
                        help="Which example to run")
    args = parser.parse_args()

    if args.action == "all":
        for name, fn in ACTIONS.items():
            log.info("--- %s ---", name)
            try:
                fn(args)
            except Exception as exc:
                log.error("Failed: %s", exc)
    else:
        ACTIONS[args.action](args)


if __name__ == "__main__":
    main()
