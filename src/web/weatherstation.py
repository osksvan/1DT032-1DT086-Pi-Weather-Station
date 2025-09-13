#
# Weather station web gui for group 16's project in course 1DT032/1DT086 at Uppsala University 
# Created 2025-09-13 
#

from flask import Flask
from flask import render_template
import random

app = Flask(__name__)

@app.route("/")
def live_data():
    # The first page you see is just the live data, currently populated with random values
    # In the template (live_data.html) this is set to auto refresh every second
    return render_template("live_data.html", temp=random.randint(-20,45))
