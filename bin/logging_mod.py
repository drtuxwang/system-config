#!/usr/bin/env python3
"""
Python log handling module

Copyright GPL v2: 2018-2024 By Dr Colin Kong
"""

import logging
import re
import unicodedata
from typing import List

RELEASE = '1.2.0'
VERSION = 20240221

LOG_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'


class ColoredFormatter(logging.Formatter):
    """
    This class handles colored formatting of logs.
    """
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
    LOG_COLORS = {
        'DEBUG': f'\x1b[1;3{CYAN}m"',
        'INFO': '\x1b[0m',
        'WARNING': f'\x1b[1;3{YELLOW}m',
        'ERROR': f'\x1b[1;3{RED}m',
        'CRITICAL': f'\x1b[1;3{MAGENTA}m',
    }

    def __init__(self, msg: str = LOG_FORMAT) -> None:
        logging.Formatter.__init__(
            self,
            f"\x1b[1;3{ColoredFormatter.GREEN}m{msg}\x1b[0m",
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

    def get(self, width: int = None) -> str:
        """
        Return compacted string with optional width.
        """
        string = self._compact(self)
        if width:
            chars = self._chars(string)
            if width > len(chars):
                chars += ' '*(width - len(chars))
            else:
                chars = chars[:width]
                if chars[-1:] == ['']:
                    chars[-1] = ' '
            string = ''.join(chars)

        return string

    def width(self) -> int:
        """
        Return compacted string width.
        """
        string = self._compact(self)
        return len(self._chars(string))


if __name__ == '__main__':
    help(__name__)
