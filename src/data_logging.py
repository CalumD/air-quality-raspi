import sys

from influxdb import InfluxDBClient


class DataLogging:
    connection_validated = False
    _local = True
    _hostname = ''
    _port = 0
    _influx = None

    def __init__(self, localhost=True, hostname='', port=0):
        if hostname.startswith('http://'):
            hostname = hostname[7:]
        elif hostname.startswith('https://'):
            hostname = hostname[8:]
        self._hostname = hostname
        self._port = port
        if not localhost:
            print(f'Trying to create a new Logger with properties: \n  host: {self._hostname}\n  port: {self._port}')
            _local = False
            self.validate()
        else:
            self.connection_validated = True

    def _init_influx_client(self):
        self._influx = InfluxDBClient(host=self._hostname, port=self._port, timeout=3)

    def validate(self):
        try:
            print('Attempting Connection...')
            self._init_influx_client()
            response = self._influx.ping()
            if response:
                print('Connection Successful')
                self.connection_validated = True
            self._influx.close()
        except Exception as err:
            print(str(err), file=sys.stderr)
