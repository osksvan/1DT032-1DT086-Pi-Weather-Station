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
import random
import os
import json

# Path to the JSON log file containing sensor data. Adjust if needed for deployment.
# LOG_FILE = "/tmp/weatherdata.json"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sensor_data.json")
# print("Using log file: {}".format(LOG_FILE))

# Configuration for data entries: (display_title, unit, json_key)
# This list defines all sensor data points to extract and plot.
# JSON keys are nested under sensor readings (e.g., {"sensors": {"temperature_celsius": value}}).
DATA_ENTRIES = [
    ("Temperature", "celsius", "temperature_celsius"),
    ("Humidity", "percent", "humidity_percent"),
    ("Pressure", "mbar", "pressure_millibars"),
    ("Yaw", "degrees", "yaw_degrees"),
    ("Pitch", "degrees", "pitch_degrees"),
    ("Roll", "degrees", "roll_degrees"),
    ("Magnetometer X", "μT", "x_microtesla"),
    ("Magnetometer Y", "μT", "y_microtesla"),
    ("Magnetometer Z", "μT", "z_microtesla"),
    ("Heading", "degrees", "compass_heading_degrees"),
    ("Acceleration X", "g", "x_g"),
    ("Acceleration Y", "g", "y_g"),
    ("Acceleration Z", "g", "z_g"),
    ("Gyro X", "rad/s", "x_rad_per_sec"),
    ("Gyro Y", "rad/s", "y_rad_per_sec"),
    ("Gyro Z", "rad/s", "z_rad_per_sec")
]

# Flask application instance
app = Flask(__name__)

# Global variable for the number of days of historical data to display (default: 30)
last_num_days = 30

@app.route("/")
@app.route('/live_data')

def live_data():
    # The first page you see is just the live data
    # In the template (live_data.html) this is set to auto refresh every second
    """
    Route for the live data page (also the Homepage).
    Extracts the most recent value for each sensor and passes it to the live_data.html template.
    The template is configured to auto-refresh every five-seconds for real-time updates.
    
    Returns:
        Rendered HTML template with current sensor values.
    """
    values = []
    for (title, unit, data_point) in DATA_ENTRIES:
        values.append((title, extract(data_point)[-1], unit))

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
        last_num_days = int(request.form.get("last_num_days"))
    
    # Draw graphs from historical data
    # Render Bokeh JavaScript and CSS resources inline for standalone embedding
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # Generate a plot for each data entry
    scripts = []
    divs = []

    timestamps = [datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f') for timestamp in extract("timestamp")]
    for (title, unit, data_point) in DATA_ENTRIES:
        temperatures = extract(data_point)

        p = figure(title=title, x_axis_label='Date', y_axis_label=unit, x_axis_type="datetime")
        p.line(timestamps[-last_num_days:], temperatures[-last_num_days:], line_width=2)
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
    
    data = get_json()
    extracted = []
    for q in data:
        for k,v in q.items():
            if k == key:
                extracted.append(v)
            if type(v) is dict:
                for kk,vv in v.items():
                    if kk == key:
                        extracted.append(vv)
    return extracted

def get_json():
    try:
        if os.path.getsize(LOG_FILE) > 0:
            with open(LOG_FILE, 'r') as file:
                dataset = json.load(file)
    except:
        print("Failed to read data")
    return dataset

if __name__ == "__main__":
    """
    Entry point when running the script directly (e.g., python weatherstation.py).
    Loads the data and prints the latest values for each sensor to the console.
    Useful for quick testing without starting the Flask server.
    """
    try:
        if os.path.getsize(LOG_FILE) > 0:
            with open(LOG_FILE, 'r') as file:
                dataset = json.load(file)
    except:
        print("Failed to read data")
    for (title, unit, data_point) in DATA_ENTRIES:
        print("{}: {} {}".format(title, extract(data_point), unit))