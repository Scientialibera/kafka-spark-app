#!/usr/bin/env python3
"""
Live GPS visualization for Sports Prophet.

Polls the API for the latest GPS coordinates and plots player positions
on a football pitch in real time using matplotlib.

Usage:
    python scripts/visualize_gps.py [--base-url URL] [--num-players N] [--run-id ID] [--duration S]
"""
import argparse
import asyncio
import itertools
import logging
import time

import aiohttp
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

PITCH_LAT_MIN = 40.0
PITCH_LAT_MAX = 40.0009
PITCH_LON_MIN = -75.0012
PITCH_LON_MAX = -75.0


async def fetch_position(session: aiohttp.ClientSession, base_url: str,
                         device_id: str, run_id: str) -> tuple[float | None, float | None]:
    url = f"{base_url}/get-topic-messages/{device_id}/{run_id}?limit=1"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                messages = data.get("messages", [])
                if messages:
                    return messages[0].get("longitude"), messages[0].get("latitude")
    except Exception as exc:
        log.error("Error fetching %s: %s", device_id, exc)
    return None, None


async def run_visualization(base_url: str, sensors: list[tuple[str, str]],
                            interval: float, duration: float) -> None:
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Live Player Positions")
    ax.set_xlim(PITCH_LON_MIN, PITCH_LON_MAX)
    ax.set_ylim(PITCH_LAT_MIN, PITCH_LAT_MAX)

    colors = itertools.cycle(["#0000FF", "#1E90FF", "#00BFFF", "#87CEFA", "#4169E1",
                               "#6495ED", "#00CED1", "#5F9EA0", "#7B68EE", "#4682B4"])
    scatter_plots = []
    for device_id, _ in sensors:
        color = next(colors)
        (plot,) = ax.plot([], [], "o", color=color, markersize=10, label=device_id)
        scatter_plots.append(plot)
    ax.legend(loc="upper right", fontsize=7)

    start = time.time()
    async with aiohttp.ClientSession() as session:
        while time.time() - start < duration:
            tasks = [fetch_position(session, base_url, did, rid) for did, rid in sensors]
            results = await asyncio.gather(*tasks)

            for i, (lon, lat) in enumerate(results):
                if lon is not None and lat is not None:
                    scatter_plots[i].set_xdata([lon])
                    scatter_plots[i].set_ydata([lat])

            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.1)
            await asyncio.sleep(interval)

    plt.ioff()
    plt.show()


def main() -> None:
    parser = argparse.ArgumentParser(description="Live GPS visualization")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--num-players", type=int, default=10, help="Number of GPS devices")
    parser.add_argument("--run-id", default="run_001", help="Run ID")
    parser.add_argument("--duration", type=int, default=60, help="Visualization duration (seconds)")
    parser.add_argument("--interval", type=float, default=1.0, help="Poll interval (seconds)")
    args = parser.parse_args()

    sensors = [(f"gps_{i}", args.run_id) for i in range(1, args.num_players + 1)]
    asyncio.run(run_visualization(args.base_url, sensors, args.interval, args.duration))


if __name__ == "__main__":
    main()
