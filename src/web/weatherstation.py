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

TEMP_LIM_MAX = 45
TEMP_LIM_MIN = -25

NUM_DATA_POINTS = 30

app = Flask(__name__)

@app.route("/")
@app.route('/live_data')
def live_data():
    # The first page you see is just the live data, currently populated with random values
    # In the template (live_data.html) this is set to auto refresh every second
    return render_template("live_data.html", temp=random.randint(TEMP_LIM_MIN,TEMP_LIM_MAX))

@app.route("/historical_data")
def historical_data():
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # Generate random example data for graphs
    # This generates two temperature readings per day for NUM_DATA_POINTS days
    x = [(datetime.now() + timedelta(day / 2)) for day in range(0, NUM_DATA_POINTS)]
    y = random.sample(range(TEMP_LIM_MIN, TEMP_LIM_MAX), NUM_DATA_POINTS)
    p = figure(title="Temperature over time", x_axis_label='Date', y_axis_label='Temperature (C)', x_axis_type="datetime")
    p.line(x, y, legend_label="Temp.", line_width=2)
    script, div = components(p)
    
    return render_template("historical_data.html",
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,)

