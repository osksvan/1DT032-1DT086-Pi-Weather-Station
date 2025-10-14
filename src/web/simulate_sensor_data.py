#!/usr/bin/env python3
"""
Simulates full Sense HAT–style sensor data for the Raspberry Pi Weather Station project.

This script mimics the JSON file format used by the real data logger on the Raspberry Pi.
It periodically writes realistic environmental, orientation, magnetometer,
accelerometer, and gyroscope values to `sensor_data.json` for testing the web UI.
"""

import json
import os
import time
import random
from datetime import datetime

# JSON log file path (same one used by Flask app)
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sensor_data.json")

# Interval between updates (seconds)
UPDATE_INTERVAL = 5

def generate_fake_sensehat_data():
    """Generate one realistic fake reading in the same structure as the real Sense HAT output."""
    yaw = random.uniform(0, 360)
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
        "environmental": {
            "temperature_celsius": round(random.uniform(18.0, 28.0), 2),
            "pressure_millibars": round(random.uniform(990.0, 1020.0), 2),
            "humidity_percent": round(random.uniform(30.0, 70.0), 2),
        },
        "orientation": {
            "yaw_degrees": round(yaw, 2),
            "pitch_degrees": round(random.uniform(-2.0, 2.0), 2),
            "roll_degrees": round(random.uniform(-2.0, 2.0), 2),
        },
        "magnetometer": {
            "x_microtesla": round(random.uniform(-40.0, 40.0), 2),
            "y_microtesla": round(random.uniform(-40.0, 40.0), 2),
            "z_microtesla": round(random.uniform(-40.0, 40.0), 2),
            "compass_heading_degrees": round(yaw, 2),
        },
        "accelerometer": {
            "x_g": round(random.uniform(-0.02, 0.02), 4),
            "y_g": round(random.uniform(-0.02, 0.02), 4),
            "z_g": round(random.uniform(0.95, 1.05), 4),
        },
        "gyroscope": {
            "x_rad_per_sec": round(random.uniform(-0.02, 0.02), 4),
            "y_rad_per_sec": round(random.uniform(-0.02, 0.02), 4),
            "z_rad_per_sec": round(random.uniform(-0.02, 0.02), 4),
        }
    }

def main():
    print(f"Simulating Sense HAT data → writing to {LOG_FILE}")
    data = []

    while True:
        entry = generate_fake_sensehat_data()
        data.append(entry)
        # keep only latest 200 readings to avoid large files
        data = data[-200:]

        try:
            with open(LOG_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[{entry['timestamp']}] Updated file ({len(data)} records)")
        except Exception as e:
            print(f"⚠️ Failed to write file: {e}")

        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()