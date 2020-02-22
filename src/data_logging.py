from influxdb import InfluxDBClient
from requests.exceptions import ConnectionError as ReqConnectionError

import utils

DB_TABLE = 'AQ_MON'
DB_USER = DB_TABLE + '_USER'
DB_PASS = DB_TABLE + '_PASS_secret'
_DB_TIMEOUT = 3


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
            self._influx = InfluxDBClient(host=self._hostname,
                                          port=self._port,
                                          username=DB_USER,
                                          password=DB_PASS,
                                          database=DB_TABLE,
                                          timeout=_DB_TIMEOUT)
            # Update the status of the db connection.
            if self._influx.ping():
                self._connection_ok = True
            else:
                self._connection_ok = False

        except ReqConnectionError:
            print('Failed to connect, reverting to local backup until connection can be initialised.')
            # TODO Validate that the filesystem allows us to write locally.

    def log_sensor_output(self, data):
        if self._local:
            print(data)
        else:
            # TODO implement persisting the data in the database.
            check_repost_unsent_values(relevant=self._local)
            print(data)


def check_repost_unsent_values(relevant=False):
    if relevant:
        print('Check for any locally stored values which weren\'t posted last time.')
        # TODO implement the rest of this branch
    else:
        print('> Skipping the check for local values because we are not persisting them anyway.')
        # TODO implement the rest of this branch
