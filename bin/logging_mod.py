#!/usr/bin/env python3
"""
Python colored log formatter

Copyright GPL v2: 2018 By Dr Colin Kong
"""

import logging
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

RELEASE = '1.0.0'
VERSION = 20180416

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'


class ColoredFormatter(logging.Formatter):
    """
    Colour codes:
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    """
    LOG_COLORS = {
        'DEBUG': '\033[1;36m',
        'INFO': '\033[0m',
        'WARNING': '\033[1;33m',
        'ERROR': '\033[1;31m',
        'CRITICAL': '\033[1;35m',
    }

    def __init__(self, msg=LOG_FORMAT):
        logging.Formatter.__init__(self, "\033[1;32m{0:s}\033[0m".format(msg))

    def format(self, record):
        record.msg = "{0:s}{1:s}\033[0m".format(
            ColoredFormatter.LOG_COLORS.get(record.levelname, ''),
            record.msg,
        )
        return super().format(record)


if __name__ == '__main__':
    help(__name__)
