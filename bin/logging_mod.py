#!/usr/bin/env python3
"""
Python colored log formatter

Copyright GPL v2: 2018-2021 By Dr Colin Kong
"""

import logging

RELEASE = '1.1.1'
VERSION = 20211107

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'


class ColoredFormatter(logging.Formatter):
    """
    Colour codes:
    """
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    LOG_COLORS = {
        'DEBUG': f'\033[1;3{CYAN}m"',
        'INFO': '\033[0m',
        'WARNING': f'\033[1;3{YELLOW}m',
        'ERROR': f'\033[1;3{RED}m',
        'CRITICAL': f'\033[1;3{MAGENTA}m',
    }

    def __init__(self, msg: str = LOG_FORMAT) -> None:
        logging.Formatter.__init__(
            self,
            f"\033[1;3{ColoredFormatter.GREEN}m{msg}\033[0m",
        )

    def format(self, record: logging.LogRecord) -> str:
        record.msg = (
            f"{ColoredFormatter.LOG_COLORS.get(record.levelname, '')}"
            f"{record.msg}\033[0m"
        )
        return super().format(record)


if __name__ == '__main__':
    help(__name__)
