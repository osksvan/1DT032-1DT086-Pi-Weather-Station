#!/usr/bin/python3

from sense_hat import SenseHat
from time import sleep, time
import numpy as np
from pathlib import Path
import math
import json
import os
from datetime import datetime

sense = SenseHat()
sense.clear()

# ---------------- CONFIG ----------------
BUFFER_SECONDS = 5
READ_INTERVAL = 0.01       # data read frequency (in seconds)
LOG_INTERVAL = 0.5         # save to JSON every 1 second
SAMPLES = int(BUFFER_SECONDS / READ_INTERVAL)
LOG_FILE = os.path.join(Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute(), "sensor_data.json")

SCROLL_SPEED = 0.05
TEXT_COLOR = (0, 255, 0)

# ---------------- BUFFERS ----------------
temp_buf, hum_buf, press_buf = [], [], []

# ---------------- STATE ----------------
modes = ["compass", "temp", "humidity", "pressure"]
mode_index = 0
last_log_time = 0

def next_mode(event):
    global mode_index
    if event.action == "pressed":
        mode_index = (mode_index + 1) % len(modes)
        sense.clear()

sense.stick.direction_middle = next_mode

# ---------------- HELPERS ----------------
def moving_average(data, window_size):
    if len(data) < window_size:
        return np.mean(data) if data else 0
    return np.mean(data[-window_size:])

def draw_compass(yaw):
    """
    Draws a 1x5 arrow pointing true north.
    Arrow rotates relative to Pi's yaw so it always points north.
    South → north: 4 white pixels, 1 red tip.
    """
    sense.clear()
    cx, cy = 3.5, 3.5
    length = 5  # total arrow pixels
    angle = math.radians(-yaw)

    arrow_pixels = []
    for i in range(length):
        x = cx + i * math.sin(angle)
        y = cy - i * math.cos(angle)
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi <= 7 and 0 <= yi <= 7:
            arrow_pixels.append((xi, yi))

    for xi, yi in arrow_pixels[:-1]:
        sense.set_pixel(xi, yi, (255, 255, 255))
    if arrow_pixels:
        tip_x, tip_y = arrow_pixels[-1]
        sense.set_pixel(tip_x, tip_y, (255, 0, 0))

def show_temp():
    temp = moving_average(temp_buf, 10)
    sense.show_message(f"T {temp:.1f}C", text_colour=TEXT_COLOR, scroll_speed=SCROLL_SPEED)

def show_humidity():
    hum = moving_average(hum_buf, 10)
    sense.show_message(f"H {hum:.1f}%", text_colour=TEXT_COLOR, scroll_speed=SCROLL_SPEED)

def show_pressure():
    press = moving_average(press_buf, 10)
    sense.show_message(f"P {press:.1f}hPa", text_colour=TEXT_COLOR, scroll_speed=SCROLL_SPEED)

def log_to_json(temp, hum, press):
    """
    Logs smoothed sensor data to JSON file with ISO-style timestamp
    and nested 'environmental' field.
    """
    data_point = {
        "timestamp": datetime.now().isoformat(),  # e.g. "2025-09-16T21:05:12.454129"
        "environmental": {
            "temperature_celsius": round(temp, 2),
            "pressure_millibars": round(press, 2),
            "humidity_percent": round(hum, 2)
        }
    }

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(data_point)

    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- MAIN LOOP ----------------
while True:
    # Gather readings
    t = sense.get_temperature()
    h = sense.get_humidity()
    p = sense.get_pressure()

    # Update buffers
    temp_buf.append(t)
    hum_buf.append(h)
    press_buf.append(p)

    if len(temp_buf) > SAMPLES:
        temp_buf.pop(0)
        hum_buf.pop(0)
        press_buf.pop(0)

    # Compute smoothed values
    temp_avg = moving_average(temp_buf, 10)
    hum_avg = moving_average(hum_buf, 10)
    press_avg = moving_average(press_buf, 10)

    # Logging every LOG_INTERVAL seconds
    if time() - last_log_time >= LOG_INTERVAL:
        log_to_json(temp_avg, hum_avg, press_avg)
        last_log_time = time()

    # Display mode logic
    mode = modes[mode_index]
    if mode == "compass":
        yaw = sense.get_orientation()["yaw"]
        draw_compass(yaw)
        sleep(0.2)
    elif mode == "temp":
        show_temp()
    elif mode == "humidity":
        show_humidity()
    elif mode == "pressure":
        show_pressure()

    sleep(READ_INTERVAL)
