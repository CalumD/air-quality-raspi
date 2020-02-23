# air-quality-raspi
This is intended to be used with a Raspberry Pi and a Bosche BME680 sensor.
The Sensor Side of the code for an air quality sensor which logs reading from the sensor and either writes them to console, or attempts to persist them in an InfluxDB database.


### Installation
First of all, on your Pi, you will need to make sure that the I2C bus is enabled, in order to let us pass data between the code and the sensor.
You can enable/disable your I2C bus by using the command below and configuring the appropriate setting: 
```(bash)
$ sudo raspi-config
```

Install the required dependencies for this project by cd'ing into the project file, then running:
```(bash)
$ pip3 install -r requirements.txt
```
You should also probably run the following in order to correctly install the SMBUS packages required to capture data from the pi's GPIO for use in python.
(Note that this step is specifically to be run on the destination machine, not a dev machine - unless that's a pi too.)
```(bash)
$ curl https://get.pimoroni.com/i2c | bash
```

### Running
There are two methods for running this project. 
Local mode, where the application will only write output to terminal; and persistent mode, where it will try to resiliently connect to a given Influx server to record data.

*IMPORTANT*, no matter which mode you choose to run the application in, you should ensure that when you run the code your (current working directory == main.py dir).
This is due to where the code writes it configuration files and backup files.
Whenever you re-run the application, you should also be in that directory.

#### Local Mode
Running in this mode will disable any persistence and only write content to terminal.
To use this mode run:
```(bash)
$ python3 src/main.py -l  (optional: -f <number> for frequency of readings)
```

#### Persistent Mode
Running the program in this mode will attempt to connect to an instance of InfluxDB running on a user-defined server provided in the command line arguments. 
See help output below for additional details:
```
usage: main.py [-h] [-v] (-l | -s) [-db DATABASE] [-p PORT] [-f FREQ]

Collect data from your BME680 sensor and optionally post it to an influxDB instance for persistence/graphing.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Display verbose console output.
  -l, --local           Choose to run the program in local only mode. (Will only log to console - not file/db.)
  -s, --save            Choose to run the program in persistence mode. (Will attempt to log all data to a remote database.)
  -db DATABASE, --database DATABASE
                        The hostname/URL/IP Address of your influxDB instance.
  -p PORT, --port PORT  The port of your influxDB instance. (1024-65535)
  -f FREQ, --freq FREQ  How many times PER HOUR, new values will be polled from the sensor.
```

#### Background Task
As this is a continually running application, you should probably set it to run in the background to allow you to keep using the system while the application gathers data.
A few common ways to do this are by using the 'screen', or 'tmux' applications.
Alternatively you can use 'nohup', and set up some bash script which is called on system startup / daemonise the application.
There are much better resources for these methods already out there than I can provide.

### Additional Configuration
#### Sensor Settings
If you know more about your environment than the defaults, you can edit the _DEFAULT_SENSOR_CONFIG object in sensor.py to better suit your environment.

#### Logging Settings
You *SHOULD* update the DB_USER and DB_PASS variables at the top of the data_logging.py file to be secure values.