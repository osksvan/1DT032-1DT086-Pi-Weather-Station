#!/usr/bin/python3
# Dummy file for generating (real) data for displaying in web
from datetime import datetime
import json
import os
import time

LOG_FILE = LOG_FILE
THERMAL_PROBE = "/sys/class/thermal/thermal_zone0/temp" 

while True:
    with open(THERMAL_PROBE, 'r') as file:
        temp = int(file.read().strip())/1000

    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w')

    if os.path.getsize(LOG_FILE) > 0:
        with open(LOG_FILE, 'r') as file:
            data = json.load(file)
    else:
        data = {}

    index = len(data)

    data[index] = {"date": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
                   "temperature": temp}

    json_str = json.dumps(data, indent=4)

    with open(LOG_FILE, 'w') as file:
        file.write(json_str)
    time.sleep(1)