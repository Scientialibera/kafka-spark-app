import requests
import matplotlib.pyplot as plt
import time

def update_coordinates(device_id: str, run_id: str, interval: float = 1.0):
    """
    Continuously fetches the latest GPS data from the Kafka stream and updates the plot with the new x, y coordinate.

    Args:
    - device_id: The ID of the device to fetch data for.
    - run_id: The run ID to fetch data for.
    - interval: How often (in seconds) to fetch new data from the API.
    """
    # Define the base URL for the FastAPI endpoint, fetching only the latest message
    base_url = f"http://localhost:8000/get-topic-messages/{device_id}/{run_id}?limit=1"

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

    scatter_plot, = ax.plot([], [], 'bo')  # Blue dot for GPS coordinate

    # Add variables to track previous coordinates
    previous_x, previous_y = None, None

    while True:
        try:
            # Fetch the latest data from the API
            response = requests.get(base_url)
            if response.status_code == 200:
                messages = response.json().get('messages', [])
                if not messages:
                    print("No new message.")
                    time.sleep(interval)
                    continue

                # Extract the latest message
                latest_message = messages[-1]

                # Extract latitude and longitude from the message
                current_x = latest_message['longitude']
                current_y = latest_message['latitude']

                # Log the received coordinates for debugging
                print(f"Received coordinates: Longitude = {current_x}, Latitude = {current_y}")

                # Check if the coordinates have changed before updating the plot
                if previous_x == current_x and previous_y == current_y:
                    print("Coordinates have not changed.")
                else:
                    # Update the plot data with the new coordinate
                    scatter_plot.set_xdata([current_x])
                    scatter_plot.set_ydata([current_y])

                    # Recompute limits if needed (optional)
                    ax.relim()
                    ax.autoscale_view()  # Automatically adjust the view limits
                    plt.draw()  # Redraw the figure
                    plt.pause(0.5)  # Pause to allow the plot to update

                    # Update previous coordinates
                    previous_x, previous_y = current_x, current_y

            else:
                print(f"Failed to get the latest message: {response.status_code}")
                print(f"Error: {response.text}")

            time.sleep(interval)  # Wait before fetching new data

        except Exception as e:
            print(f"Error while fetching data: {e}")
            break

    plt.ioff()  # Turn off interactive mode
    plt.show()  # Keep the plot open when the loop ends

if __name__ == "__main__":
    update_coordinates("gps_1", "run_001", interval=1.0)
