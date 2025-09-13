#
# Weather station web gui for group 16's project in course 1DT032/1DT086 at Uppsala University 
# Created 2025-09-13 
#

from flask import Flask, render_template
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import INLINE
from datetime import datetime, timedelta
import random
import os
import json

LOG_FILE = "/tmp/weatherdata.json"

app = Flask(__name__)

@app.route("/")
@app.route('/live_data')
def live_data():
    # The first page you see is just the live data
    # In the template (live_data.html) this is set to auto refresh every second
    (_, temperatures) = get_data()
    return render_template("live_data.html", temp=temperatures[-1])

@app.route("/historical_data")
def historical_data():
    # Draw graphs from historical data
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    (timestamps, temperatures) = get_data()
    p = figure(title="Temperature over time", x_axis_label='Date', y_axis_label='Temperature (C)', x_axis_type="datetime")
    p.line(timestamps, temperatures, legend_label="Temp.", line_width=2)
    script, div = components(p)

    return render_template("historical_data.html",
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,)

def get_data():
    # Read data from LOG_FILE, return data as separate lists
    while True:
        try:
            if os.path.getsize(LOG_FILE) > 0:
                with open(LOG_FILE, 'r') as file:
                    dataset = json.load(file)
                break
        except:
            print("Failed to read data")
    timestamps = []
    temperatures = []

    for index in dataset:
        data = dataset[index]
        timestamps.append(datetime.strptime(data["date"], '%Y-%m-%dT%H:%M:%S.%f'))
        temperatures.append(data["temperature"])
    return (timestamps, temperatures)