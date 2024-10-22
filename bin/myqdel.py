#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job deletion.
"""

import argparse
import os
import signal
import socket
import sys
from pathlib import Path
from typing import List

from task_mod import Tasks

RELEASE = '3.2.0'
VERSION = 20241021


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_all_flag(self) -> str:
        """
        Return all flag.
        """
        return self._args.all_flag

    def get_force_flag(self) -> bool:
        """
        Return force flag.
        """
        return self._args.force_flag

    def get_jobids(self) -> List[int]:
        """
        Return list of job IDs.
        """
        return self._jobids

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description=f"MyQS v{RELEASE}, "
            "My Queuing System batch job deletion.",
        )

        parser.add_argument(
            '-v',
            '-V',
            '-version',
            '--version',
            action='version',
            version=f"MyQS {RELEASE} ({VERSION})",
        )
        parser.add_argument(
            '-a',
            dest='all_flag',
            action='store_true',
            help="Purge all completed jobs.",
        )
        parser.add_argument(
            '-k',
            action='store_true',
            dest='force_flag',
            help="Force termination of running jobs.",
        )
        parser.add_argument(
            'jobIds',
            nargs='*',
            metavar='jobid',
            help="Batch job ID.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._jobids = []
        for jobid in self._args.jobIds:
            if not jobid.isdigit() or int(jobid) < 1:
                raise SystemExit(f'{sys.argv[0]}: Invalid "{jobid}" job ID.')
            self._jobids.append(int(jobid))


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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _get_info(path: Path) -> dict:
        info = {}
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        info[key] = value
        except OSError:
            return {}
        return info

    def _remove(self, jobid: int) -> None:
        for status in 'dfq':
            path = Path(self._myqsdir, f'{jobid}.{status}')
            info = self._get_info(path)
            if info.get('COMMAND'):
                try:
                    path.unlink()
                except OSError:
                    continue
                print(f"MyQS jobid {jobid} deleted: {info['COMMAND']}")
                return

        path = Path(self._myqsdir, f'{jobid}.r')
        info = self._get_info(path)
        if info.get('COMMAND'):
            if self._force_flag:
                try:
                    Tasks.factory().killpgid(
                        int(info.get('PGID', '')),
                        signame='TERM',
                    )
                except ValueError:
                    pass
                try:
                    path.unlink()
                except OSError:
                    pass
                print(
                    f"MyQS jobid {jobid} killed and deleted: {info['COMMAND']}"
                )
            else:
                print(f"MyQS jobid {jobid} is running: {info['COMMAND']}")

    def _purge(self) -> None:
        for jobid in sorted(
            [int(x.stem) for x in self._myqsdir.glob('*.[df]')]
        ):
            self._remove(jobid)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._force_flag = options.get_force_flag()

        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine home directory.",
            )
        self._myqsdir = Path(
            Path.home(),
            '.config',
            'myqs',
            socket.gethostname().split('.')[0].lower()
        )
        for jobid in options.get_jobids():
            if not list(Path(self._myqsdir).glob(f'{jobid}.[dfqr]')):
                print(f"MyQS jobid {jobid} does not exists.")
            else:
                self._remove(jobid)
        if options.get_all_flag():
            self._purge()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
