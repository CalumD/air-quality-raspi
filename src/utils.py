import sys

verbose = True


def v_print(content):
    # if verbose:
    print(content)


def early_quit(reason='An unexpected error occurred and the program had to terminate'):
    print(f'{reason}', file=sys.stderr)
    exit(1)


def clean_shutdown(sig, frame):
    # TODO implement some clean shutdown logic if we are using a remote connection or are writing to file.
    print('You pressed Ctrl+C!')
    exit(0)
