#!/usr/bin/python3
"""
Weather Station Web GUI for Group 16's project in course 1DT032/1DT086 at Uppsala University.
This application provides a Flask-based web interface to display live and historical weather
data from a JSON log file, visualized using Bokeh plots.

Authors: Group 16
Created: 2025-09-13
Version: 1.0.0
Dependencies: flask, bokeh, python-dateutil
"""

from flask import Flask, render_template, request
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from datetime import datetime, timedelta
from pathlib import Path
import random
import os
import json
import time

# Path to the JSON log file containing sensor data. Adjust if needed.
# LOG_FILE = "/tmp/weatherdata.json"
LOG_FILE = os.path.join(Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute(), "sensor_data.json")

# Configuration for data entries: (display_title, unit, json_key)
# This list defines all sensor data points to extract and plot.
# JSON keys are nested under sensor readings (e.g., {"sensors": {"temperature_celsius": value}}).
DATA_ENTRIES = [
    ("Temperature", "celsius", "temperature_celsius"),
    ("Humidity", "percent", "humidity_percent"),
    ("Pressure", "mbar", "pressure_millibars"),
    #("Yaw", "degrees", "yaw_degrees"),
    #("Pitch", "degrees", "pitch_degrees"),
    #("Roll", "degrees", "roll_degrees"),
    #("Magnetometer X", "μT", "x_microtesla"),
    #("Magnetometer Y", "μT", "y_microtesla"),
    #("Magnetometer Z", "μT", "z_microtesla"),
    #("Heading", "degrees", "compass_heading_degrees"),
    #("Acceleration X", "g", "x_g"),
    #("Acceleration Y", "g", "y_g"),
    #("Acceleration Z", "g", "z_g"),
    #("Gyro X", "rad/s", "x_rad_per_sec"),
    #("Gyro Y", "rad/s", "y_rad_per_sec"),
    #("Gyro Z", "rad/s", "z_rad_per_sec")
]

# Flask application instance
app = Flask(__name__)

# Global variable for the number of days of historical data to display (default: 30)
last_num_days = 30

@app.route("/")
@app.route('/live_data')

def live_data():
    """
    Route for the live data page (Homepage).
    Extracts the most recent value for each sensor and passes it to the live_data.html template.
    The template is configured to auto-refresh every five-seconds for real-time updates.
    
    Returns:
        Rendered HTML template with current sensor values.
    """
    values = []
    for (title, unit, data_point) in DATA_ENTRIES:
        # Prevents a 500 error if get_json() returns [] or a key has no data.
        series = extract(data_point)
        latest = series[-1] if series else None  
        values.append((title, latest, unit))

    return render_template("live_data.html", values=values)

@app.route("/historical_data", methods =["GET", "POST"])
def historical_data():
    """
    Route for the historical data page.
    Supports POST to update the number of days to display.
    Generates Bokeh line plots for each sensor over the selected time period.
    
    Handles:
        - GET: Render current view with default/previous num_days.
        - POST: Update last_num_days from form data.
    
    Returns:
        Rendered HTML template with embedded Bokeh plots and resources.
    """
    
    global last_num_days
    if request.method == "POST":
        # Update the global num_days from form input (e.g., from a slider or input field)
        user_input = request.form.get("last_num_days")
        try:
            last_num_days = min(max(int(user_input), 1), 100000)
        except:
            print(f"Failed to parse '{user_input}' as int.")
    
    # Draw graphs from historical data
    # Render Bokeh JavaScript and CSS resources inline for standalone embedding
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # Generate a plot for each data entry
    scripts = []
    divs = []

    # Get all timestamps then out only last n days worth of data
    timestamps = [datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f') for timestamp in extract("timestamp")]
    timestamps = [ts for ts in timestamps if ts >= datetime.now() - timedelta(days=last_num_days)]

    for (title, unit, data_point) in DATA_ENTRIES:
        values = extract(data_point)

        if len(timestamps):

            p = figure(title=title, x_axis_label='Date', y_axis_label=unit, x_axis_type="datetime")
            p.line(timestamps, values[-len(timestamps):], line_width=2)
            script, div = components(p)

            scripts.append(script)
            divs.append(div)

    return render_template("historical_data.html",
        plot_scripts=scripts,
        plot_divs=divs,
        js_resources=js_resources,
        css_resources=css_resources,
        last_num_days=last_num_days,)

def extract(key):
    """
    Extracts all values for a given key from the JSON dataset.
    Handles both top-level keys and nested keys (e.g., under a 'sensors' dict).
    
    Args:
        key (str): The JSON key to extract (e.g., 'temperature_celsius').
    
    Returns:
        list: List of extracted values, in chronological order.
              Empty list if no data or key not found.
    """
    
    data = get_json()
    if not data:
        return []

    extracted = []
    for entry in data:
        # Check top-level keys
        if key in entry:
            extracted.append(entry[key])
        # Check nested dicts (e.g., entry['sensors'][key])
        for value in entry.values():
            if isinstance(value, dict):
                if key in value:
                    extracted.append(value[key])
    return extracted    

def get_json(max_retries=30, sleep_seconds=0.1):
    """
    Loads the weather data from the JSON log file, robustly.

    Behavior:
        - If file is missing or empty: return [].
        - If JSON is temporarily invalid/half-written: retry in a loop
          until it becomes valid or we reach max_retries, then return [].
        - Always returns a list (parsed dataset) or [].

    Args:
        max_retries (int): maximum retry attempts before giving up.
        sleep_seconds (float): sleep interval between retries.

    Returns:
        list: The parsed JSON data (list of dicts), or [] on failure.
    """
    attempts = 0
    while True:
        try:
            if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
                return []

            # Read full text first, then parse (avoids some edge cases)
            with open(LOG_FILE, "r") as f:
                text = f.read()

            data = json.loads(text)  # may raise JSONDecodeError

            # Structure check: we expect a list of entries
            if isinstance(data, list):
                return data
            else:
                print(f"[get_json] Invalid structure (expected list, got {type(data).__name__}); retrying...")

        except (json.JSONDecodeError, OSError) as e:
            # Likely half-written file or transient IO error; retry
            print(f"[get_json] transient read error: {e}")
            pass

        attempts += 1
        if attempts >= max_retries:
            print(f"[get_json] Giving up after {attempts} attempts; returning [].")
            return []

        time.sleep(sleep_seconds)

if __name__ == "__main__":
    """
    Entry point when running the script directly (e.g., python weatherstation.py).
    Loads the data and prints the latest values for each sensor to the console.
    Useful for quick testing without starting the Flask server.
    """
    # Load data for printing
    dataset = get_json()
    if dataset:
        print("Latest sensor readings:")
        for (title, unit, data_point) in DATA_ENTRIES:
            values = extract(data_point)
            if values:
                latest = values[-1]
                print(f"{title}: {latest} {unit}")
            else:
                print(f"{title}: No data available")
    else:
        print("No data loaded. Ensure data.json exists and is valid.")
