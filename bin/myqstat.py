#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job status.
"""

import argparse
import json
import os
import signal
import socket
import sys
import time
from pathlib import Path
from typing import List

from command_mod import Command
from logging_mod import Message
from subtask_mod import Exec, Task
from task_mod import Tasks

RELEASE = '3.1.3'


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

    def get_width(self) -> int:
        """
        Return stdout width.
        """
        try:
            return os.get_terminal_size().columns
        except OSError:  # stdout closed
            return int(os.environ['COLUMNS'])

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


class Status:
    """
    Status class
    """

    def __init__(self) -> None:
        self._lines: dict = {
            'DONE': [],
            'FAIL': [],
            'RUN':  [],
            'STOP':  [],
            'QUEUE': [],
        }

    def add(self, mode: str, lines: List[str]) -> None:
        """
        Add job output lines.
        """
        self._lines[mode].extend(lines)

    def show(self) -> None:
        """
        Show job status
        """
        print(
            "JOBID  QUEUE   JOBNAME               "
            "( MyQS v3)               CPUS  STATE  TIME"
        )
        for mode in ('DONE', 'FAIL', 'RUN', 'STOP', 'QUEUE'):
            for line in self._lines[mode]:
                print(line)


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
                    if Tasks.factory().haspid(pid):
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
        info['LINES'] = json.loads(info.get('OUTPUT', '[]'))

        # Determine last two output lines
        try:
            log_path = Path(info['LOGFILE'])
            with log_path.open('rb') as ifile:
                ifile.seek(max(0, log_path.stat().st_size - 1024))
                data = ifile.read(1024)
        except (KeyError, OSError):
            pass
        else:
            if b'\n' not in data:
                lines = [data.decode(errors='replace').rstrip()]
            elif path.suffix == '.r':
                lines = data.decode(errors='replace').split('\n')[-3:-1]
            else:
                lines = data.decode(errors='replace').rstrip().split('\n')[-2:]
            info['LINES'] = [Message(x).get() for x in lines]

        return info

    def _get_lines(self, info: dict, options: Options) -> List[str]:
        lines = []
        if options.get_full_flag():
            lines.append(f"\x1b[1;35mMyQS DIRECTORY   = {info['DIRECTORY']}")
            lines.append(f"MyQS COMMAND     = {info['COMMAND']}\x1b[0m")
            if 'LOGFILE' in info:
                lines.append(
                    f"\x1b[1;35mMyQS LOGFILE     = {info['LOGFILE']}\x1b[0m"
                )
            if 'PGID' in info:
                lines.append(
                    f"\x1b[1;35mMyQS PGID        = {info['PGID']}\x1b[0m"
                )

        for message in [Message(x) for x in info['LINES']]:
            if message.width() > options.get_width():
                message = message.get(options.get_width(), lcut=True)
            lines.append(f"\x1b[1;34m{message}\x1b[0m")
        return lines

    def _showjobs(self, options: Options) -> None:
        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine home directory.",
            )

        jobids = options.get_jobids()
        modes = (
             ('DONE', 'FAIL', 'QUEUE')
             if options.get_all_flag() or jobids else
             ('QUEUE',)
        )
        if not jobids:
            jobids = sorted(
                [int(x.stem) for x in self._myqsdir.glob('*.[dfqr]')]
            )

        status = Status()
        for jobid in sorted(jobids):
            for mode in modes:
                path = Path(self._myqsdir, f'{jobid}.{mode[0].lower()}')
                info = self._get_info(path)
                if info:
                    job_name = Message(info.get('JOBNAME')).get(45, lcut=True)
                    status.add(
                        mode,
                        [
                            f"{jobid:5d}  {info.get('QUEUE', ''):7s} "
                            f"{job_name}        "
                            f"{mode:5s}{info.get('ETIME'):>6s}"
                        ] + self._get_lines(info, options)
                    )
                    continue
            info = self._get_info(Path(self._myqsdir, f'{jobid}.r'))
            if info:
                job_name = Message(info.get('JOBNAME')).get(45, lcut=True)
                pgid = int(info.get('PGID', '0'))
                if not Tasks.factory().haspgid(pgid):
                    time.sleep(0.1)
                    if not Tasks.factory().haspgid(pgid):
                        status.add(
                            'STOP',
                            [
                                f"\x1b[1;33m{jobid:5d}  "
                                f"{info.get('QUEUE', ''):7s}"
                                f" {job_name}  {info.get('NCPUS', 1):>3s}   "
                                "STOP      -\x1b[0m"
                            ] + self._get_lines(info, options)
                        )
                        continue
                status.add(
                    'RUN',
                    [
                        f"\x1b[1;33m{jobid:5d}  {info.get('QUEUE', ''):7s} "
                        f"{job_name}  {info.get('NCPUS', 1):>3s}   RUN  "
                        f"{info.get('ETIME'):>6s}\x1b[0m"
                    ] + self._get_lines(info, options)
                )
        status.show()

    @staticmethod
    def _watch() -> None:
        watch = Command('watch', errors='stop')
        watch.set_args(['--interval', '10', '--color', __file__])
        Exec(watch.get_cmdline()).run()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        if options.get_watch_flag():
            self._watch()

        try:
            self.width = os.get_terminal_size().columns
        except OSError:
            self.width = int(os.environ['COLUMNS'])  # stdout closed

        host = socket.gethostname().split('.')[0].lower()
        self._myqsdir = Path(Path.home(), '.config', 'myqs', host)
        self._showjobs(options)

        if not self._has_myqsd():
            myqsd = Command('myqsd', args=['1'], errors='stop')
            Task(myqsd.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
