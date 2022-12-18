#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job deletion.
"""

import argparse
import glob
import os
import signal
import socket
import sys
from pathlib import Path
from typing import List

import task_mod

RELEASE = '2.8.7'


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._release = RELEASE
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_force_flag(self) -> bool:
        """
        Return force flag.
        """
        return self._args.force_flag

    def get_jobids(self) -> List[str]:
        """
        Return list of job IDs.
        """
        return self._jobids

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description=f"MyQS v{self._release}, "
            "My Queuing System batch job deletion.",
        )

        parser.add_argument(
            '-k',
            action='store_true',
            dest='force_flag',
            help="Force termination of running jobs.",
        )
        parser.add_argument(
            'jobIds',
            nargs='+',
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
            if not jobid.isdigit():
                raise SystemExit(f'{sys.argv[0]}: Invalid "{jobid}" job ID.')
            self._jobids.append(jobid)


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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _remove(self, jobid: str) -> None:
        path = Path(self._myqsdir, f'{jobid}.q')
        if path.is_file():
            try:
                path.unlink()
            except OSError:
                pass
            else:
                print(
                    'Batch job with jobid',
                    jobid,
                    'has been deleted from MyQS.'
                )
                return
        path = Path(self._myqsdir, f'{jobid}.r')
        if path.is_file():
            try:
                with path.open(encoding='utf-8', errors='replace') as ifile:
                    if not self._force_flag:
                        print(
                            'MyQS cannot delete batch job with jobid',
                            jobid,
                            'as it is running.'
                        )
                    else:
                        info = {}
                        for line in ifile:
                            line = line.strip()
                            if '=' in line:
                                info[line.split('=')[0]] = (
                                    line.split('=', 1)[1])
                        if 'PGID' in info:
                            try:
                                pgid = int(info['PGID'])
                            except ValueError:
                                return
                            task_mod.Tasks.factory(
                                ).killpgid(pgid, signal='TERM')
                        try:
                            path.unlink()
                        except OSError:
                            pass
                        print(
                            'Batch job with jobid',
                            jobid,
                            'has been deleted from MyQS.'
                        )
            except OSError:
                pass

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
            if not Path(self._myqsdir).glob(f'{jobid}.[qr]'):
                print(
                    'MyQS cannot delete batch job with jobid',
                    jobid,
                    'as it does no exist.',
                )
            else:
                self._remove(jobid)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
