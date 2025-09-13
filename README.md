# Project in course 1DT032/1DT086 at Uppsala University

This project uses a Raspberry Pi version 3B and the Pi Sense HAT to collect data about the environment.

## Running the Web GUI

To run the web gui, start it by running `flask --app weatherstation run` from the `src/web` directory.
This is used to run the app with debug, do not use in production. To access the web, open the following in your web browser: http://127.0.0.1:5000

You may need to install python3 and flask, on debian based systems this is usually done by running `apt install python3.XX python3-flask`, replace XX with the current supported version of python for your operating system. For whatever reason, bokeh is not available through apt, and must be installed in another way. Look up how to install for your circumstances, or if you do not care about potentially breaking your computers python environment, you may install using `pip install bokeh --break-system-packages`.