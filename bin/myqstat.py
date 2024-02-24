#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job status.
"""

import argparse
import os
import signal
import socket
import sys
import time
from pathlib import Path
from typing import List

import command_mod
import logging_mod
import subtask_mod
import task_mod

RELEASE = '3.1.0'


class Options:
    """
    Options class
    """
    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_all_flag(self) -> bool:
        """
        Return all flag.
        """
        return self._args.all_flag

    def get_full_flag(self) -> bool:
        """
        Return full flag.
        """
        return self._args.full_flag

    def get_watch_flag(self) -> bool:
        """
        Return watch flag.
        """
        return self._args.watch_flag

    def get_jobids(self) -> List[int]:
        """
        Return list of job IDs.
        """
        return self._jobids

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description=f"MyQS v{RELEASE}, "
            "My Queuing System batch job status.",
        )

        parser.add_argument(
            '-a',
            dest='all_flag',
            action='store_true',
            help="Show all jobs (include finished jobs).",
        )
        parser.add_argument(
            '-f',
            dest='full_flag',
            action='store_true',
            help="Show full job information.",
        )
        parser.add_argument(
            '-w',
            dest='watch_flag',
            action='store_true',
            help="Watch batch jobs continuously.",
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

    def _has_myqsd(self) -> bool:
        path = Path(self._myqsdir, 'myqsd.pid')
        try:
            with path.open(errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if task_mod.Tasks.factory().haspid(pid):
                        return True
                    path.unlink()
        except OSError:
            pass
        return False

    @classmethod
    def _get_info(cls, path: Path) -> dict:
        info: dict = {}
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        info[key] = value
        except OSError:
            return {}

        # Determine run elapsed time
        start = float(info.get('START', '0'))
        if path.suffix in ('.d', '.f'):
            elapsed = float(info.get('FINISH', '0')) - start
        elif path.suffix == '.r':
            elapsed = time.time() - start
        else:
            elapsed = -1
        info['ETIME'] = f'{int(elapsed)}' if elapsed >= 0 else '-'

        # Determine last output line
        try:
            log_path = Path(info['LOGFILE'])
            with log_path.open('rb') as ifile:
                ifile.seek(max(0, log_path.stat().st_size - 1024))
                data = ifile.read(1024)
        except (KeyError, OSError):
            info['OUTPUT'] = []
        else:
            if b'\n' not in data:
                lines = [data.decode(errors='replace').rstrip()]
            elif path.suffix == '.r':
                lines = data.decode(errors='replace').split('\n')[-3:-1]
            else:
                lines = data.decode(errors='replace').rstrip().split('\n')[-2:]
            info['OUTPUT'] = [logging_mod.Message(x).get() for x in lines]

        return info

    @staticmethod
    def _show_info(info: dict, full: bool) -> None:
        if full:
            print(f"\x1b[1;35mMyQS DIRECTORY   = {info['DIRECTORY']}")
            print(f"MyQS COMMAND     = {info['COMMAND']}\x1b[0m")
            if 'LOGFILE' in info:
                print(f"\x1b[1;35mMyQS LOGFILE     = {info['LOGFILE']}\x1b[0m")
            if 'PGID' in info:
                print(f"\x1b[1;35mMyQS PGID        = {info['PGID']}\x1b[0m")

        for line in info['OUTPUT']:
            print(f"\x1b[1;34m{line}\x1b[0m")

    def _showjobs(self, options: Options) -> None:
        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine home directory.",
            )
        print(
            "JOBID  QUEUE   JOBNAME               "
            "( MyQS v3)               CPUS  STATE  TIME"
        )

        jobids = options.get_jobids()
        statuses = (
             ('DONE', 'FAIL', 'QUEUE')
             if options.get_all_flag() or jobids else
             ('QUEUE',)
        )
        if not jobids:
            jobids = sorted(
                [int(x.stem) for x in self._myqsdir.glob('*.[dfqr]')]
            )

        for jobid in sorted(jobids):
            for status in statuses:
                path = Path(self._myqsdir, f'{jobid}.{status[0].lower()}')
                info = self._get_info(path)
                if info:
                    job_name = logging_mod.Message(info.get('JOBNAME')).get(45)
                    print(
                        f"{jobid:5d}  {info.get('QUEUE', ''):7s} "
                        f"{job_name}        {status:5s}{info.get('ETIME'):>6s}"
                    )
                    self._show_info(info, options.get_full_flag())
                    continue
            info = self._get_info(Path(self._myqsdir, f'{jobid}.r'))
            if info:
                job_name = logging_mod.Message(info.get('JOBNAME')).get(45)
                pgid = int(info.get('PGID', '0'))
                if not task_mod.Tasks.factory().haspgid(pgid):
                    time.sleep(0.1)
                    if not task_mod.Tasks.factory().haspgid(pgid):
                        print(
                            f"\x1b[1;33m{jobid:5d}  {info.get('QUEUE', ''):7s}"
                            f" {job_name}  {info.get('NCPUS', 1):>3s}   "
                            "STOP      -\x1b[0m"
                        )
                        self._show_info(info, options.get_full_flag())
                        continue
                print(
                    f"\x1b[1;33m{jobid:5d}  {info.get('QUEUE', ''):7s} "
                    f"{job_name}  {info.get('NCPUS', 1):>3s}   RUN  "
                    f"{info.get('ETIME'):>6s}\x1b[0m"
                )
                self._show_info(info, options.get_full_flag())

    @staticmethod
    def _watch() -> None:
        watch = command_mod.Command('watch', errors='stop')
        watch.set_args(['--interval', '10', '--color', __file__])
        subtask_mod.Exec(watch.get_cmdline()).run()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if options.get_watch_flag():
            self._watch()

        host = socket.gethostname().split('.')[0].lower()
        self._myqsdir = Path(Path.home(), '.config', 'myqs', host)
        self._showjobs(options)

        if self._has_myqsd():
            return 0
        print('\nMyQS batch job scheduler not running. Run "myqsd" command.')
        return 1


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
