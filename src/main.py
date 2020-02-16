#!/usr/bin/env python3
import argparse
import sched
import signal

from data_logging import DataLogging
from sensor import Sensor

verbose = False
logger = DataLogging()
sensor = Sensor


def get_commandline_args():
    """
    Collects various arguments from the command line to decide how the application should operate.
    :return: An object containing the accepted, parsed, arguments.
    """

    # Create the base parser
    argument_parser = argparse.ArgumentParser(description="Collect data from your BME680 sensor and optionally post "
                                                          "it to an influxDB instance for persistence/graphing.")

    # Allow the output to be verbose.
    argument_parser.add_argument("-v", "--verbose",
                                 help="Display verbose console output.",
                                 action="store_true",
                                 default=False)

    # Add a group to make the user choose between local and persistence.
    mode_group = argument_parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-l", "--local",
                            help="Choose to run the program in local only mode. (Will only log to console - not "
                                 "file/db.)",
                            action="store_true",
                            default=False)
    mode_group.add_argument("-s", "--save",
                            help="Choose to run the program in persistence mode. (Will attempt to log all data to a "
                                 "remote database.)",
                            action="store_true",
                            default=False)

    # Add arguments for the remote logging server.
    argument_parser.add_argument("-db", "--database",
                                 type=str,
                                 help="The hostname/URL/IP Address of your influxDB instance.",
                                 default="localhost")
    argument_parser.add_argument("-p", "--port",
                                 type=int,
                                 help="The port of your influxDB instance. (1024-65535)",
                                 default=8086)

    # Add an argument to set the frequency of polling
    argument_parser.add_argument("-f", "--freq",
                                 type=int,
                                 help="How many times PER HOUR, new values will be polled from the sensor.",
                                 default=60)  # Once per minute

    parsed_arguments = argument_parser.parse_args()
    global verbose
    verbose = parsed_arguments.verbose
    return parsed_arguments


def validate_commandline_args(parsed_arguments):
    # Validate the port number
    if not (1024 < parsed_arguments.port <= 65535):
        print('Command line port number must be between 1025 and 65535.')
        return False

    # Validate frequency is sensible
    if not (1 <= parsed_arguments.freq <= 3600):
        print('Polling Frequency must be at least 1 (1/Hour), and at most 3600 (1/Second)')
        return False

    # Validate the database connection
    global logger
    if parsed_arguments.save:
        logger = DataLogging(localhost=False, hostname=parsed_arguments.database, port=parsed_arguments.port)
    else:
        logger = DataLogging(localhost=True)

    # Everything was successfully validated so respond True.
    return True


def execute(freq):
    # Calculate the work delay based on the polling frequency
    one_hour = 3600
    polling_frequency = one_hour // freq  # Floor division to get the nearest int.
    v_print(f'Calculated Polling to run every {polling_frequency} seconds')

    # Do a 'Run-Once'
    work()

    # Begin perpetual execution.
    scheduler = sched.scheduler()
    while True:
        scheduler.enter(delay=polling_frequency, priority=1, action=work)
        scheduler.run()


def work():
    # Get data from sensor
    sensor_output = sensor.read()

    # Send data to logger
    logger.log_sensor_output(data=sensor_output)


def v_print(content):
    if verbose:
        print(content)


def clean_shutdown(sig, frame):
    # TODO implement some clean shutdown logic if we are using a remote connection or are writing to file.
    print('You pressed Ctrl+C!')
    exit(0)


signal.signal(signal.SIGINT, clean_shutdown)
signal.signal(signal.SIGTERM, clean_shutdown)
if __name__ == '__main__':
    print('Checking command line arguments...')
    parsed_args = get_commandline_args()
    v_print('> Got command line arguments successfully.\n')

    v_print('Validating command line arguments...')
    if not validate_commandline_args(parsed_args):
        exit(1)
    v_print('> Validated the command line arguments are okay.\n')

    v_print('Setup Sensor...')
    sensor = Sensor()
    v_print('> Sensor Initialised.\n')

    print('-- Operational --')
    execute(parsed_args.freq)
