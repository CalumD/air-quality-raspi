import json
import os.path
import sys
import time
from datetime import datetime

verbose = True


def v_print(content):
    if verbose:
        print(content)


def early_quit(reason='An unexpected error occurred and the program had to terminate'):
    print(f'{reason}', file=sys.stderr)
    exit(1)


def clean_shutdown(sig, frame):
    # TODO implement some clean shutdown logic if we are using a remote connection or are writing to file.
    print('You pressed Ctrl+C!')
    exit(0)


def validate_can_write_file(path):
    if os.path.exists(path):
        if not os.path.isfile(path):
            early_quit(f'Destination for file, {path} is marked as a directory, quitting.')
    try:
        with open(path, 'w') as test_file:
            test_file.write('')
        os.remove(path)
        return True
    except Exception:
        early_quit(f'No write permissions allowed to config file destination, {path}, quitting.')


def validate_file_exists(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            if os.access(path, os.R_OK):
                return True
            else:
                early_quit(f'File {path} was un-readable at runtime, quitting.')
        else:
            early_quit(f'Destination for file, {path} was marked as a directory, quitting.')
    else:
        return False


def get_json_from_file(path):
    try:
        with open(path, 'r') as json_file:
            config_data = json.load(json_file)
    except Exception as err:
        early_quit(f'Something went wrong trying to get config from {path}, {str(err)}')
    return config_data


class DataCapture:
    timestamp = time.time()

    def __init__(self, temperature=0.0, humidity=0.0, pressure=0.0, gas=0.0, iaq_index=0.0):
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.gas = gas
        self.iaq_index = iaq_index

    def tick(self):
        self.timestamp = time.time()

    def __str__(self):
        return '{0}: ' 'Temp {1:.2f}°C, Humidity {2:.2f} %RH, Pressure {3:.2f} hPa, ' \
               'Gas Resistance {4:.2f} Ohms, Quality Index: {5:.2f}' \
            .format(datetime.fromtimestamp(self.timestamp).strftime('%d/%m/%Y %T.%f')[:-3],
                    self.temperature, self.humidity, self.pressure, self.gas, self.iaq_index)
