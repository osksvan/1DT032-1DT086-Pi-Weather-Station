# Project in course 1DT032/1DT086 at Uppsala University

This project uses a Raspberry Pi version 3B and the Pi Sense HAT to collect data about the environment.

## Running the Web GUI

To run the web gui, start it by running `flask --app weatherstation run` from the `src/web` directory.
This is used to run the app with debug, do not use in production. To access the web, open the following in your web browser: http://127.0.0.1:5000

You may need to install python3 and flask, on debian based systems this is usually done by running `apt install python3.XX python3-flask`, replace XX with the current supported version of python for your operating system. For whatever reason, bokeh is not available through apt, and must be installed in another way. Look up how to install for your circumstances, or if you do not care about potentially breaking your computers python environment, you may install using `pip install bokeh --break-system-packages`.

## Installing systemd services
The systemd unit files are located in this repository under `systemd`.
Since they contain special keyword `%h`, they need to be placed in the user's systemd directory, this was done to avoid running as root and to simplify for different users.

    cd    # Leave blank, this is for $HOME
    git clone https://github.com/osksvan/1DT032-1DT086-Pi-Weather-Station.git
    cd 1DT032-1DT086-Pi-Weather-Station/systemd
    mkdir -p ~/.config/systemd/user/ && cp *.service "$_"
    systemctl --user enable webapp.service
    systemctl --user start webapp.service
    systemctl --user enable backend.service
    systemctl --user start backend.service

