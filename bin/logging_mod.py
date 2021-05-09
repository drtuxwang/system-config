#!/usr/bin/env python3
"""
Python colored log formatter

Copyright GPL v2: 2018-2021 By Dr Colin Kong
"""

import logging

RELEASE = '1.1.0'
VERSION = 20210509

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'


class ColoredFormatter(logging.Formatter):
    """
    Colour codes:
    """
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    LOG_COLORS = {
        'DEBUG': '\033[1;3{0:d}m"'.format(CYAN),
        'INFO': '\033[0m',
        'WARNING': '\033[1;3{0:d}m'.format(YELLOW),
        'ERROR': '\033[1;3{0:d}m'.format(RED),
        'CRITICAL': '\033[1;3{0:d}m'.format(MAGENTA),
    }

    def __init__(self, msg: str = LOG_FORMAT) -> None:
        logging.Formatter.__init__(self, "\033[1;3{0:d}m{1:s}\033[0m".format(
            ColoredFormatter.GREEN,
            msg,
        ))

    def format(self, record: logging.LogRecord) -> str:
        record.msg = "{0:s}{1:s}\033[0m".format(
            ColoredFormatter.LOG_COLORS.get(record.levelname, ''),
            record.msg,
        )
        return super().format(record)


if __name__ == '__main__':
    help(__name__)
