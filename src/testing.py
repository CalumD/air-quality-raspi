import argparse

from data_logging import DataLogging

verbose = False
logger = {}


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
    # Validate the database connection
    global logger
    if parsed_arguments.save:
        logger = DataLogging(localhost=False, hostname=parsed_arguments.database, port=parsed_arguments.port)
    else:
        logger = DataLogging(localhost=True)
    return logger.connection_validated


def check_repost_unsent_values(relevant=False):
    if relevant:
        print('Check for any locally stored values which weren\'t posted last time.')
        # TODO implement the rest of this branch
    else:
        print('> Skipping the check for local values because we are not persisting them anyway.')
        # Also remove any previous record file as it will be outdated by the time it may be wanted again.
        # TODO implement the rest of this branch


def execute():
    print('Start doing the actual logic.')
    # TODO Call out to the sensor code to get set up and schedule polling the data from the sensor.
    pass


def v_print(content):
    if verbose:
        print(content)


if __name__ == '__main__':
    print('Checking command line arguments...')
    parsed_args = get_commandline_args()
    v_print('> Got command line arguments successfully.\n')

    v_print('Validating command line arguments...')
    if not validate_commandline_args(parsed_args):
        exit(1)
    v_print('> Validated the command line arguments are okay.\n')

    v_print('Checking if we need to re-post any values which failed to persist...')
    check_repost_unsent_values(parsed_args.save)
    v_print('> Dealt with any unsent values.\n')

    print('-- Operational --')
    execute()
