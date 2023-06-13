import datetime
import os

# Description: Common functions for the project that are used in multiple files

workdir = os.path.dirname(__file__)


def log_message(message):
    with open(f'{workdir}/logs.txt', 'a') as f:
        timestamp = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        f.write(f'{timestamp}: {message}\n')
