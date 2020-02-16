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
$ python3 src/main.py -l
```

#### Persistent Mode
Running the program in this mode will attempt to connect to a persistence provider as defined in the command line arguments. See help output below:
```
usage: main.py [-h] [-v] (-l | -s) [-db DATABASE] [-p PORT] [-f FREQ]

Collect data from your BME680 sensor and optionally post it to an influxDB
instance for persistence/graphing.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Display verbose console output.
  -l, --local           Choose to run the program in local only mode. (Will
                        only log to console - not file/db.)
  -s, --save            Choose to run the program in persistence mode. (Will
                        attempt to log all data to a remote database.)
  -db DATABASE, --database DATABASE
                        The hostname/URL/IP Address of your influxDB instance.
  -p PORT, --port PORT  The port of your influxDB instance. (1024-65535)
  -f FREQ, --freq FREQ  How many times PER HOUR, new values will be polled
                        from the sensor.
```
