#!/usr/bin/env python3
"""
Python log handling module

Copyright GPL v2: 2018-2024 By Dr Colin Kong
"""

import logging
import re
import sys
import unicodedata
from typing import List

RELEASE = '1.4.1'
VERSION = 20241026

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'


class ColoredFormatter(logging.Formatter):
    """
    This class handles colored formatting of logs.
    """
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    LOG_COLORS = {
        'DEBUG': f'\x1b[1;3{BLUE}m',
        'INFO': '\x1b[0m',
        'WARNING': f'\x1b[1;3{YELLOW}m',
        'ERROR': f'\x1b[1;3{RED}m',
        'CRITICAL': f'\x1b[1;3{MAGENTA}m',
    }

    def __init__(self, msg: str = LOG_FORMAT) -> None:
        logging.Formatter.__init__(
            self,
            f"\x1b[1;3{ColoredFormatter.GREEN}m{msg}\x1b[0m",
            datefmt='%Y-%m-%dT%H:%M:%S%z',
        )

    def format(self, record: logging.LogRecord) -> str:
        record.msg = (
            f"{ColoredFormatter.LOG_COLORS.get(record.levelname, '')}"
            f"{record.msg}\x1b[0m"
        )
        return super().format(record)


class Message(str):
    """
    This class handles str with double width characters.
    """
    isjunk = re.compile('\x1b]0;[^\x07]*\x07')  # xterm title

    @classmethod
    def _compact(cls, string: str) -> str:
        chars: list = []
        start = 0
        pos = 0
        for char in cls.isjunk.sub('', string):
            if char == '\b':  # Move left
                if pos > start:
                    pos -= 1
            elif char == '\r':  # Move to line start
                pos = start
            else:
                chars[pos:pos+1] = [char]
                pos += 1
                if char == "\n":
                    start = pos
        return ''.join(chars)

    @staticmethod
    def _chars(string: str) -> List[str]:
        chars: list = []
        pos = 0
        for char in string:
            # East Asian Wide & Full-width
            if unicodedata.east_asian_width(char) in 'WF':
                chars[pos:pos+2] = ['', char]
                pos += 2
            else:
                chars[pos:pos+1] = [char]
                pos += 1
        return chars

    def get(
        self,
        width: int = 0,
        lcut: bool = False,
        lpad: bool = False,
    ) -> 'Message':
        """
        Return compacted string with optional width.
        """
        string = self._compact(self)
        if width:
            chars = self._chars(string)
            if len(chars) < width:
                if lpad:  # Left padding
                    chars = [' ']*(abs(width) - len(chars)) + chars
                else:     # Right padding
                    chars.extend([' ']*(width - len(chars)))
            elif lcut:    # Left truncate
                chars = chars[-width:]
                if chars[1:2] == ['']:
                    chars[0] = ' '
            else:         # Right truncate
                chars = chars[:width]
                if chars[-1:] == ['']:
                    chars[-1] = ' '
            string = ''.join(chars)

        return Message(string)

    def width(self) -> int:
        """
        Return compacted string width.
        """
        string = self._compact(self)
        return len(self._chars(string))


if __name__ == '__main__':
    if sys.argv[-1] in ('-v', '-V', '-version', '--version'):
        print(f"Python log handling module {RELEASE} ({VERSION})")
    else:
        help(__name__)

        logger = logging.getLogger(__name__)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)

        logger.debug('This is debug logging message example')
        logger.info('This is info logging message example')
        logger.warning('This is warning logging message example')
        logger.error('This is error logging message example')
        logger.critical('This is critical logging message example')
