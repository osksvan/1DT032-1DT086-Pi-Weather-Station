#!/usr/bin/python3
#
# Weather station web gui for group 16's project in course 1DT032/1DT086 at Uppsala University 
# Created 2025-09-13 
#

from flask import Flask, render_template, request
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from datetime import datetime, timedelta
import random
import os
import json

# LOG_FILE = "/tmp/weatherdata.json"
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sensor_data.json")
print("Using log file: {}".format(LOG_FILE))

DATA_ENTRIES = [("Temperature", "celsius", "temperature_celsius"),
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
                ("Gyro Z", "rad/s", "z_rad_per_sec")]

app = Flask(__name__)

last_num_days = 30

@app.route("/")
@app.route('/live_data')
def live_data():
    # The first page you see is just the live data
    # In the template (live_data.html) this is set to auto refresh every second
    values = []
    for (title, unit, data_point) in DATA_ENTRIES:
        values.append((title, extract(data_point)[-1], unit))

    return render_template("live_data.html", values=values)

@app.route("/historical_data", methods =["GET", "POST"])
def historical_data():
    global last_num_days
    if request.method == "POST":
        last_num_days = int(request.form.get("last_num_days"))
    # Draw graphs from historical data
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

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
    try:
        if os.path.getsize(LOG_FILE) > 0:
            with open(LOG_FILE, 'r') as file:
                dataset = json.load(file)
    except:
        print("Failed to read data")
    for (title, unit, data_point) in DATA_ENTRIES:
        print("{}: {} {}".format(title, extract(data_point), unit))