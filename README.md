# air-quality-raspi
The Sensor Side of the client/server code for an air quality sensor which logs details to a graphing application.
This is intended to be used with a Raspberry Pi and a Bosche BME680 sensor.


### Installation
Install the required dependencies for this project by cd'ing into the project file, then running:
```(bash)
$ pip3 install -r requirements.txt
```


### Running
There are two methods for running this project. Temporary mode, where the application will only run for as long as the command is running in terminal; and persistent mode, where it will try to resiliently connect to a given server to carry out the logging of the outputs.

#### Temporary Mode
Running in this mode will disable any persistence and only write content to terminal.
To use this mode run:
```(bash)
$ python3 src/main.py
```

#### Persistent Mode
Running the program in this mode will attempt to connect to a persistence provider as declared in the 'config.json' file; which consists of a hostname and a port with the accompanying server side code [see here!](https://github.com/CalumD/air-quality-grapher)
In the case where a connection can not be made, the data will be written locally, and will bulk upload when the connection is re-established.
To use this mode run:
```(bash)
$ python3 src/main.py -p
```
