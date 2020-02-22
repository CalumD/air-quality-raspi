import os
import pickle
import uuid
from datetime import datetime

from influxdb import InfluxDBClient
from requests.exceptions import ConnectionError as ReqConnectionError

import utils

_DB_FAILED_WRITES = 'failed_db_writes.dbp'
DB_TABLE = 'AQ_MON'
DB_USER = DB_TABLE + '_USER'
DB_PASS = DB_TABLE + '_PASS_secret'
_DB_TIMEOUT = 3
_PROG_RUN_ID = uuid.uuid4()
_HOST_NAME = utils.HOST_NAME


class DataLogging:
    _local = True
    _hostname = ''
    _port = 8086
    _influx = None
    _connection_ok = False

    def __init__(self, hostname='', port=8086):
        # Check for localhost
        if hostname != '':
            # Running remotely:
            self._local = False
            # Truncate protocol at start of hostname, if exists.
            if hostname.startswith('http://'):
                hostname = hostname[7:]
            elif hostname.startswith('https://'):
                hostname = hostname[8:]
            self._hostname = hostname
            self._port = port

        # Attempt the connection to see if properties exist, and create them if not.
        if not self._local:
            self._init_influx_client()

    def _init_influx_client(self):
        try:
            utils.validate_can_write_file(_DB_FAILED_WRITES)
            # Connect to the server
            print(f'Attempting connection to host \'{self._hostname}:{self._port}\'')
            self._influx = InfluxDBClient(host=self._hostname, port=self._port, timeout=_DB_TIMEOUT)

            # Check for the user existence
            user_found = False
            for user in self._influx.get_list_users():
                if user['user'] == DB_USER:
                    user_found = True
            if not user_found:
                utils.v_print('Influx user not found, creating...')
                self._influx.create_user(username=DB_USER, password=DB_PASS)
            else:
                utils.v_print('Identified Influx User...')

            # Check for the database existence
            db_found = False
            for db in self._influx.get_list_database():
                if db['name'] == DB_TABLE:
                    db_found = True
            if not db_found:
                utils.v_print('Influx table not found, creating...')
                self._influx.create_database(dbname=DB_TABLE)
            else:
                utils.v_print('Identified Influx Collection...')

            # Applying database permissions to the user
            if (not user_found) or (not db_found):
                self._influx.grant_privilege(privilege='ALL', database=DB_TABLE, username=DB_USER)

            # Check for a retention policy
            # TODO Implement some sort of retention policy.
            pass

            # Reset the connection with appropriate user data.
            self._influx.close()
            self._connect()

        except ReqConnectionError:
            self._connection_ok = False
            print('Failed to connect, reverting to local backup until connection can be initialised.')

    def _connect(self):
        self._influx = InfluxDBClient(host=self._hostname,
                                      port=self._port,
                                      username=DB_USER,
                                      password=DB_PASS,
                                      database=DB_TABLE,
                                      timeout=_DB_TIMEOUT)
        # Update the status of the db connection.
        if self._influx.ping():
            self._connection_ok = True
            print(f'Connection to {self._hostname}:{self._port} successful.')
        else:
            raise ReqConnectionError('Unable to ping the database.')

    def log_sensor_output(self, data: utils.DataCapture):
        if not self._local:
            if self._connection_ok:
                self._write_remote(data)
            else:
                self._init_influx_client()
                if self._connection_ok:
                    self._check_repost_unsent_values()
                    self._write_remote(data)
                else:
                    self._write_local(data)
        print(data)

    def _check_repost_unsent_values(self):
        if not utils.validate_file_exists(_DB_FAILED_WRITES):
            return
        utils.v_print('Had values which were not successfully sent.')
        for data in self._load_locals():
            if self._connection_ok:
                self._write_remote(data)
            else:
                self._write_local(data)

    def _write_remote(self, data: utils.DataCapture):
        try:
            self._influx.write_points([
                {
                    "time": f'{datetime.fromtimestamp(data.timestamp).strftime("%Y-%m-%dT%T.%f")[:-3]}Z',
                    "measurement": "AQ",
                    "tags": {
                        "runID": _PROG_RUN_ID,
                        "hostname": _HOST_NAME
                    },
                    "fields": {
                        "temperature": data.temperature,
                        "humidity": data.humidity,
                        "pressure": data.pressure,
                        "gas": data.gas,
                        "quality": data.iaq_index
                    }
                }
            ])
        except Exception as err:
            utils.v_print(err)
            self._influx.close()
            self._connection_ok = False
            self._write_local(data)

    def _write_local(self, data: utils.DataCapture):
        self._write_locals([data])

    @staticmethod
    def _write_locals(data: [utils.DataCapture]):
        with open(_DB_FAILED_WRITES, 'ab') as db_backups:
            for val in data:
                pickle.dump(val, db_backups)

    @staticmethod
    def _load_locals() -> [utils.DataCapture]:
        backups = []
        with open(_DB_FAILED_WRITES, 'rb') as db_backups:
            while True:
                try:
                    backups.append(pickle.load(db_backups))
                except EOFError:
                    break
        os.remove(_DB_FAILED_WRITES)
        return backups
