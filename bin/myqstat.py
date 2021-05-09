#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job statistics.
"""

import argparse
import glob
import os
import signal
import socket
import sys
import time
from typing import List

import task_mod

RELEASE = '2.8.1'


class Options:
    """
    Options class
    """
    def __init__(self) -> None:
        self._release = RELEASE
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_release(self) -> str:
        """
        Return release version.
        """
        return self._release

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release +
            ', My Queuing System batch job submission.',
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

    def _myqsd(self) -> None:
        lockfile = os.path.join(self._myqsdir, 'myqsd.pid')
        try:
            with open(lockfile, errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if task_mod.Tasks.factory().haspid(pid):
                        return
                    os.remove(lockfile)
        except OSError:
            pass
        print('MyQS batch job scheduler not running. Run "myqsd" command.')

    def _showjobs(self) -> None:
        print(
            'JOBID  QUEUENAME  JOBNAME                                     '
            'CPUS  STATE  TIME'
        )
        jobids: List[int] = []
        for file in glob.glob(os.path.join(self._myqsdir, '*.[qr]')):
            try:
                jobids.append(int(os.path.basename(file)[:-2]))
            except ValueError:
                pass

        info: dict = {}
        for jobid in sorted(jobids):
            try:
                state = 'QUEUE'
                with open(
                    os.path.join(self._myqsdir, str(jobid) + '.q'),
                    errors='replace'
                ) as ifile:
                    for line in ifile:
                        line = line.strip()
                        if '=' in line:
                            info[line.split('=')[0]] = line.split('=', 1)[1]
            except OSError:
                try:
                    with open(
                        os.path.join(self._myqsdir, str(jobid) + '.r'),
                        errors='replace'
                    ) as ifile:
                        for line in ifile:
                            line = line.strip()
                            if '=' in line:
                                info[line.split('=')[0]] = (
                                    line.split('=', 1)[1]
                                )
                except OSError:
                    continue
                state = 'RUN'
            if 'NCPUS' in info:
                self._show_details(info, jobid, state)
        print()

    @staticmethod
    def _show_details(info: dict, jobid: int, state: str) -> None:
        output: List[str] = []
        if 'START' in info:
            try:
                etime = str(int((time.time() - float(info['START'])) / 60.))
                pgid = int(info['PGID'])
            except ValueError:
                etime = '0'
            else:
                if task_mod.Tasks.factory().haspgid(pgid):
                    if os.path.isdir(info['DIRECTORY']):
                        logfile = os.path.join(
                            info['DIRECTORY'],
                            os.path.basename(info['COMMAND']) +
                            '.o' + str(jobid)
                        )
                    else:
                        logfile = os.path.join(
                            os.environ['HOME'],
                            os.path.basename(info['COMMAND']) +
                            '.o' + str(jobid)
                        )
                    try:
                        with open(logfile, errors='replace') as ifile:
                            output = []
                            for line in ifile:
                                output = (output + [line.rstrip()])[-5:]
                    except OSError:
                        pass
                else:
                    state = 'STOP'
        else:
            etime = '-'
        print("{0:5d}  {1:9s}  {2:42s}  {3:>3s}   {4:5s} {5:>5s}".format(
            jobid,
            info['QUEUE'],
            info['COMMAND'],
            info['NCPUS'],
            state,
            etime,
        ))
        for line in output:
            print(line)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        host = socket.gethostname().split('.')[0].lower()
        print(
            '\nMyQS', options.get_release(),
            ', My Queuing System batch job statistics on HOST "' +
            host + '".\n'
        )
        if 'HOME' not in os.environ:
            raise SystemExit(
                sys.argv[0] + ': Cannot determine home directory.')
        self._myqsdir = os.path.join(
            os.environ['HOME'], '.config', 'myqs', host)
        self._showjobs()
        self._myqsd()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
