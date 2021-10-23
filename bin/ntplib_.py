#!/usr/bin/env python3
"""
Set the date and time via NTP pool
"""

import argparse
import glob
import logging
import os
import signal
import socket
import sys
import time
from typing import List

import numpy
import ntplib  # type: ignore

import command_mod
import file_mod
import logging_mod
import subtask_mod

CONNECTIONS = 16

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_delay(self) -> int:
        """
        Return retry delay.
        """
        return self._delay

    def get_server(self) -> str:
        """
        Return list of files.
        """
        return self._args.server[0]

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Set the date and time via NTP pool',
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Do not apply but Show average offset only.'
        )
        parser.add_argument(
            'server',
            nargs=1,
            help='NTP server pool (ie "uk.pool.ntp.org").'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        newest = file_mod.FileUtil.newest(glob.glob('/etc/*'))
        time_stamp = file_mod.FileStat(newest).get_time()
        if time_stamp - time.time() > 86400:
            logger.warning(
                "Current clock is too old (Please check CMOS battery)",
            )
            self._delay = 10
        else:
            self._delay = 60


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def get_offset(server: str) -> float:
        """
        Determine NTP offset
        """
        client = ntplib.NTPClient()
        offsets = []
        logger.info("Connecting to NTP servers: {0:s}".format(server))
        for _ in range(CONNECTIONS):
            try:
                response = client.request(server, version=3)
            except (socket.gaierror, ntplib.NTPException):
                logger.info("Offset:    ?.?????????  (???.???.???.???)")
            else:
                logger.info("Offset:   {0:12.9f}  ({1:s})".format(
                    response.offset,
                    ntplib.ref_id_to_text(response.ref_id),
                ))
                offsets.append(response.offset)

        if len(offsets) >= 4:
            mean = numpy.mean(offsets)
            stddev = numpy.std(offsets)
            offsets = [x for x in offsets if abs(x - mean) < 2*stddev]
            if len(offsets) > 4:
                if abs(max(offsets) - min(offsets) < 60.):
                    average = numpy.mean(offsets)
                    logger.info("Average:  {0:12.9f}  ({1:d} rejected)".format(
                        average,
                        CONNECTIONS - len(offsets),
                    ))
                    return average
                logger.error("Unstable: offset range is over a minute")
        return None

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        server = options.get_server()
        delay = options.get_delay()
        if options.get_view_flag():
            cls.get_offset(server)
            return 0

        date = command_mod.Command('date')
        hwclock = command_mod.Command('hwclock', errors='stop')

        while True:
            offset = cls.get_offset(server)
            if offset:
                break
            logger.error("Failure:  retrying in {0:d} seconds".format(delay))
            time.sleep(delay)

        logger.info("Updating: System clock with offset...")
        subtask_mod.Task(date.get_cmdline() + [
            '+%Y-%m-%d %H:%M:%S.%N%z',
            '--set',
            '{0:f} sec'.format(offset),
        ]).run()

        logger.info("Syncing:  Setting hardware clock...")
        subtask_mod.Task(hwclock.get_cmdline() + ['--systohc']).run()
        subtask_mod.Task(hwclock.get_cmdline() + ['--show']).run()
        logger.info("DONE!")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
