import argparse


def get_commandline_args():
    """
    Collects various arguments from the command line to decide how the application should operate.
    :return: An object containing the accepted, parsed, arguments.
    """
    # Create the base parser
    argument_parser = argparse.ArgumentParser(description="Collect data from your BME680 sensor and optionally post "
                                                          "it to an influxDB instance for persistence/graphing.")
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
                                 help="The port of your influxDB instance.",
                                 default=8086)
    # Add an argument to set the frequency of polling
    argument_parser.add_argument("-f", "--freq",
                                 type=int,
                                 help="How many times PER HOUR, new values will be polled from the sensor.")
    return argument_parser.parse_args()


def check_repost_unsent_values(relevant=False):
    if relevant:
        print('Check for any locally stored values which weren\'t posted last time.')
    else:
        print('Skipping the check for local values because we are not persisting them anyway.')


def execute():
    print('Start doing the actual logic.')
    pass


if __name__ == '__main__':
    parsed_args = get_commandline_args()
    check_repost_unsent_values(parsed_args.save)
    execute()
