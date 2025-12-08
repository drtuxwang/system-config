#!/usr/bin/env python3
"""
Set the date and time via NTP pool
"""

import argparse
import glob
import logging
import math
import signal
import socket
import statistics
import sys
import time
from typing import Generator, List

import dns.resolver  # type: ignore
import ntplib  # type: ignore

from command_mod import Command
from file_mod import FileStat, FileUtil
from logging_mod import ColoredFormatter
from subtask_mod import Task

DNS_SERVERS = [
    '2606:4700:4700::1111',
    '2001:4860:4860::8888',
    '1.1.1.1',
    '8.8.8.8',
]
NTP_SERVER = 'pool.ntp.org'
NTP_SYNC_MAX = 8
NTP_SYNC_MIN = 3
NTP_SYNC_REPEAT = 3600

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_repeat_flag(self) -> bool:
        """
        Return repeat flag.
        """
        return self._args.repeat_flag

    def get_update_flag(self) -> bool:
        """
        Return update flag.
        """
        return self._args.update_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Set the date and time via NTP pool",
        )

        parser.add_argument(
            '-r',
            dest='repeat_flag',
            action='store_true',
            help=f"Repeat time sync every {NTP_SYNC_REPEAT} seconds.",
        )
        parser.add_argument(
            '-u',
            dest='update_flag',
            action='store_true',
            help="Apply average offset calculated.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def check_clock(self) -> int:
        """
        Check clock and apply rough correction. Return retry time.
        """
        logger.info("Checking current clock...")
        newest = FileUtil.newest(glob.glob('/etc/*'))
        mtime = FileStat(newest).get_mtime()
        if mtime - time.time() > 86400:
            logger.info("Updating: System clock setting...")
            Task(self._date.get_cmdline() + [
                '+%Y-%m-%dT%H:%M:%S.%N%z',
                '--set',
                f'@{mtime:f}',
            ]).run()
            logger.info("Syncing:  Setting hardware clock...")
            Task(self._hwclock.get_cmdline() + ['--systohc']).run()
            Task(self._hwclock.get_cmdline() + ['--show']).run()
            return 10

        return 60

    @staticmethod
    def get_server() -> Generator[str, None, None]:
        """
        Return NTP server IP address
        """
        client = dns.resolver.Resolver(configure=False)
        client.nameservers = DNS_SERVERS
        while True:
            try:
                for answer in client.resolve(NTP_SERVER, 'A'):
                    yield answer.to_text()
            except dns.exception.DNSException:
                yield 'none'

    @classmethod
    def get_offset(cls) -> float:
        """
        Determine NTP offset
        """
        client = ntplib.NTPClient()
        offsets = []
        logger.info("Connecting to NTP server...")
        for _ in range(NTP_SYNC_MAX):
            try:
                response = client.request(next(cls.get_server()), version=3)
            except (socket.gaierror, ntplib.NTPException):
                logger.info("Offset:    ?.?????????  (???.???.???.???)")
            else:
                logger.info(
                    "Offset:   %12.9f  (%s)",
                    response.offset,
                    ntplib.ref_id_to_text(response.ref_id),
                )
                offsets.append(response.offset)

        if len(offsets) >= NTP_SYNC_MIN:
            mean = statistics.mean(offsets)
            stddev = statistics.pstdev(offsets)
            offsets = [
                x
                for x in offsets
                if math.isclose(mean, x, abs_tol=2*stddev)
            ]
            if len(offsets) > NTP_SYNC_MIN:
                if math.isclose(min(offsets), max(offsets), abs_tol=60.):
                    average = statistics.mean(offsets)
                    logger.info(
                        "Average:  %12.9f  (%d rejected)",
                        average,
                        NTP_SYNC_MAX - len(offsets),
                    )
                    return average
                logger.error("Unstable: offset range is over a minute")
        return None

    def set_clock(self, offset: float) -> None:
        """
        Check clock and apply rough correction. Return retry time.
        """
        logger.info("Updating: System clock with offset...")
        Task(self._date.get_cmdline() + [
            '+%Y-%m-%dT%H:%M:%S.%N%z',
            '--set',
            f'{offset} sec',
        ]).run()

        logger.info("Syncing:  Setting hardware clock...")
        Task(self._hwclock.get_cmdline() + ['--systohc']).run()
        Task(self._hwclock.get_cmdline() + ['--show']).run()

    def run(self) -> int:
        """
        Start program
        """
        logger.info("NTPLIB starting...")
        logger.info("NTPLIB DNS Servers: %s", DNS_SERVERS)
        logger.info("NTPLIB NTP Server:  %s", NTP_SERVER)

        options = Options()
        if not options.get_update_flag():
            self.get_offset()
            return 0

        self._date = Command('date', errors='stop')
        self._hwclock = Command('hwclock', errors='stop')
        delay = self.check_clock()

        while True:
            offset = self.get_offset()
            if offset:
                self.set_clock(offset)
                if options.get_repeat_flag():
                    logger.info(
                        "Synced:   Resyncing in %d seconds.",
                        NTP_SYNC_REPEAT,
                    )
                    time.sleep(NTP_SYNC_REPEAT)
                    continue
                break
            logger.error("Failure:  retrying in %d seconds", delay)
            time.sleep(delay)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
