import sys

from influxdb import InfluxDBClient


class DataLogging:
    _local = True
    _hostname = ''
    _port = 0
    _influx = None

    def __init__(self, localhost=True, hostname='', port=0):
        if hostname.startswith('http://'):
            hostname = hostname[7:]
        elif hostname.startswith('https://'):
            hostname = hostname[8:]
        self._local = localhost
        self._hostname = hostname
        self._port = port
        if not localhost:
            print(f'Trying to create a new Logger with properties: \n  host: {self._hostname}\n  port: {self._port}')
            _local = False
            self.validate()

    def _init_influx_client(self):
        self._influx = InfluxDBClient(host=self._hostname, port=self._port, timeout=3)

    def validate(self):
        try:
            print('Attempting Connection...')
            self._init_influx_client()
            response = self._influx.ping()
            if response:
                print('Connection Successful')
            else:
                # TODO implement what to do if the connection was not successful.
                pass
            self._influx.close()
        except Exception as err:
            print(str(err), file=sys.stderr)

    def log_sensor_output(self, data):
        timestamp = time.time()

        def __init__(self, temperature=0.0, humidity=0.0, pressure=0.0, gas=0.0, iaq_index=0.0):
            self.temperature = temperature
            self.humidity = humidity
            self.pressure = pressure
            self.gas = gas
            self.iaq_index = iaq_index

        # TODO implement the logging
        print(f'TS: {data.timestamp},  Temp: {data.temperature},  Humidity: {data.humidity},  Pres: {data.pressure},  '
              f'gas: {data.gas},  IAQ: {data.iaq_index}.')


def check_repost_unsent_values(relevant=False):
    if relevant:
        print('Check for any locally stored values which weren\'t posted last time.')
        # TODO implement the rest of this branch
    else:
        print('> Skipping the check for local values because we are not persisting them anyway.')
        # TODO implement the rest of this branch
