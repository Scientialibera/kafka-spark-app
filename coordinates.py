import asyncio
import aiohttp
import json
import matplotlib.pyplot as plt
import itertools
import time

async def fetch_latest_message(session, device_id, run_id):
    """
    Asynchronously fetch the latest coordinates for a given device_id and run_id from the API.
    Fetch only the latest message.
    """
    url = f"http://127.0.0.1:8000/get-topic-messages/{device_id}/{run_id}?limit=1"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                response_json = await response.json()
                messages = response_json.get('messages', [])
                if messages:
                    return messages[0]['longitude'], messages[0]['latitude']
            else:
                print(f"Error fetching messages for {device_id}, {run_id}: {response.status}")
    except Exception as e:
        print(f"An error occurred while fetching {device_id}, {run_id}: {e}")
    
    return None, None  # Return None if no valid data was fetched

async def update_coordinates(sensors: list, interval: float, runtime: float):
    """
    Continuously fetch the latest GPS data from the Kafka stream for multiple sensors
    and update the plot with their respective coordinates in different shades of blue.

    Args:
    - sensors: List of tuples with (device_id, run_id) for each sensor.
    - interval: How often (in seconds) to fetch new data from the API.
    - runtime: Total running time in seconds for the visualization.
    """
    # Football pitch boundaries in lat/lon
    PITCH_LAT_MIN = 40.0
    PITCH_LAT_MAX = 40.0009  # Approx. 100m in latitude degrees
    PITCH_LON_MIN = -75.0012
    PITCH_LON_MAX = -75.0  # Approx. 64m in longitude degrees

    # Initialize the plot
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Set initial plot limits based on the football pitch boundaries
    ax.set_xlim(PITCH_LON_MIN, PITCH_LON_MAX)
    ax.set_ylim(PITCH_LAT_MIN, PITCH_LAT_MAX)

    # Generate different shades of blue for each sensor
    colors = itertools.cycle(['#0000FF', '#1E90FF', '#00BFFF', '#87CEFA'])

    # Initialize scatter plots for each sensor
    scatter_plots = []
    for sensor in sensors:
        color = next(colors)
        scatter_plot, = ax.plot([], [], 'o', color=color, markersize=10)  # Create a scatter plot for each sensor
        scatter_plots.append(scatter_plot)

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        while time.time() - start_time < runtime:
            tasks = []
            for i, (device_id, run_id) in enumerate(sensors):
                # Fetch the latest coordinates asynchronously for each sensor
                task = asyncio.create_task(fetch_latest_message(session, device_id, run_id))
                tasks.append(task)

            # Gather results from all sensors
            results = await asyncio.gather(*tasks)

            # Update plot with the latest data
            for i, (current_x, current_y) in enumerate(results):
                if current_x is not None and current_y is not None:
                    scatter_plots[i].set_xdata([current_x])
                    scatter_plots[i].set_ydata([current_y])

            # Redraw and update the plot
            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.1)  # Pause to allow the plot to update

            await asyncio.sleep(interval)  # Wait for the next update

    plt.ioff()  # Turn off interactive mode
    plt.show()  # Keep the plot open when the loop ends

if __name__ == "__main__":
    # Define the 10 sensors (device_id: "gps_1", run_id: "run_001" to "run_010")
    sensors = [(f"gps_1", f"run_{str(i).zfill(3)}") for i in range(1, 5)]

    # Define parameters
    runtime = 60  # Total running time in seconds
    interval = 1   # Time interval between updates (in seconds)

    # Run the asyncio loop
    asyncio.run(update_coordinates(sensors, interval, runtime))
