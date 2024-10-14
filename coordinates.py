import requests
import matplotlib.pyplot as plt
import time
import itertools

def update_coordinates(sensors: list, interval: float = 1.0):
    """
    Continuously fetches the latest GPS data from the Kafka stream for multiple teammates
    and updates the plot with their respective coordinates in different shades of blue.

    Args:
    - sensors: List of tuples with (device_id, run_id) for each teammate.
    - interval: How often (in seconds) to fetch new data from the API.
    """
    # Football pitch boundaries
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

    # Generate different shades of blue for each teammate
    colors = itertools.cycle(['#0000FF', '#1E90FF', '#00BFFF', '#87CEFA'])  # Different shades of blue

    # Initialize scatter plots for each teammate
    scatter_plots = []
    for sensor in sensors:
        color = next(colors)
        scatter_plot, = ax.plot([], [], 'o', color=color)  # Create a scatter plot for each sensor
        scatter_plots.append(scatter_plot)

    # Add variables to track previous coordinates for each sensor
    previous_coordinates = [None] * len(sensors)

    while True:
        for i, (device_id, run_id) in enumerate(sensors):
            try:
                # Define the base URL for the FastAPI endpoint, fetching only the latest message
                base_url = f"http://localhost:8000/get-topic-messages/{device_id}/{run_id}?limit=1"

                # Fetch the latest data from the API
                response = requests.get(base_url)
                if response.status_code == 200:
                    messages = response.json().get('messages', [])
                    if not messages:
                        print(f"No new message for {device_id}, {run_id}.")
                        continue

                    # Extract the latest message
                    latest_message = messages[-1]

                    # Extract latitude and longitude from the message
                    current_x = latest_message['longitude']
                    current_y = latest_message['latitude']

                    # Log the received coordinates for debugging
                    print(f"Received coordinates for {device_id}, {run_id}: Longitude = {current_x}, Latitude = {current_y}")

                    # Check if the coordinates have changed before updating the plot
                    if previous_coordinates[i] == (current_x, current_y):
                        print(f"Coordinates for {device_id}, {run_id} have not changed.")
                    else:
                        # Update the plot data with the new coordinate for this sensor
                        scatter_plots[i].set_xdata([current_x])
                        scatter_plots[i].set_ydata([current_y])

                        # Update previous coordinates
                        previous_coordinates[i] = (current_x, current_y)

                else:
                    print(f"Failed to get the latest message for {device_id}, {run_id}: {response.status_code}")
                    print(f"Error: {response.text}")

            except Exception as e:
                print(f"Error while fetching data for {device_id}, {run_id}: {e}")

        # Recompute limits if needed (optional)
        ax.relim()
        ax.autoscale_view()  # Automatically adjust the view limits
        plt.draw()  # Redraw the figure
        plt.pause(0.1)  # Pause to allow the plot to update

        time.sleep(interval)  # Wait before fetching new data

    plt.ioff()  # Turn off interactive mode
    plt.show()  # Keep the plot open when the loop ends


if __name__ == "__main__":
    # Example usage with two teammates
    teammates = [("gps_1", "run_001"), ("gps_1", "run_002")]
    update_coordinates(teammates, interval=.1)
