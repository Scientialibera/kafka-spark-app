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

    # Initialize the plot
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    scatter_plot, = ax.plot([], [], 'bo')  # Blue dot for GPS coordinate

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

                # Assuming the messages are ordered from oldest to newest
                latest_message = messages[-1]

                # Extract latitude and longitude from the message
                current_x = latest_message['longitude']
                current_y = latest_message['latitude']

                # Update the plot data with the new coordinate
                scatter_plot.set_xdata([current_x])
                scatter_plot.set_ydata([current_y])
                ax.relim()  # Recompute the data limits based on the current data
                ax.autoscale_view()  # Automatically adjust the view limits
                plt.draw()  # Redraw the figure
                plt.pause(0.01)  # Pause to allow the plot to update

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
