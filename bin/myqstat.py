#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job statistics.
"""

import argparse
import os
import signal
import socket
import sys
import time
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

    def get_release(self) -> str:
        """
        Return release version.
        """
        return self._release

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description=f"MyQS v{self._release}, "
            "My Queuing System batch job submission.",
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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    def _myqsd(self) -> None:
        path = Path(self._myqsdir, 'myqsd.pid')
        try:
            with path.open(errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if task_mod.Tasks.factory().haspid(pid):
                        return
                    path.unlink()
        except OSError:
            pass
        print('MyQS batch job scheduler not running. Run "myqsd" command.')

    def _showjobs(self) -> None:
        print(
            'JOBID  QUEUENAME  JOBNAME                                     '
            'CPUS  STATE  TIME'
        )
        jobids: List[int] = []
        for path in self._myqsdir.glob('*.[qr]'):
            try:
                jobids.append(int(path.stem))
            except ValueError:
                pass

        info: dict = {}
        for jobid in sorted(jobids):
            try:
                state = 'QUEUE'
                path = Path(self._myqsdir, f'{jobid}.q')
                with path.open(errors='replace') as ifile:
                    for line in ifile:
                        line = line.strip()
                        if '=' in line:
                            info[line.split('=')[0]] = line.split('=', 1)[1]
            except OSError:
                try:
                    path = Path(self._myqsdir, f'{jobid}.r')
                    with path.open(errors='replace') as ifile:
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
                    if Path(info['DIRECTORY']).is_dir():
                        log_path = Path(
                            info['DIRECTORY'],
                            f"{Path(info['COMMAND']).name}.o{jobid}",
                        )
                    else:
                        log_path = Path(
                            Path.home(),
                            f"{Path(info['COMMAND']).name}.o{jobid}",
                        )
                    try:
                        with log_path.open(errors='replace') as ifile:
                            output = []
                            for line in ifile:
                                output = (output + [line.rstrip()])[-5:]
                    except OSError:
                        pass
                else:
                    state = 'STOP'
        else:
            etime = '-'
        print(
            f"{jobid:5d}  {info['QUEUE']:9s}  {info['COMMAND']:42s}  "
            f"{info['NCPUS']:>3s}   {state:5s} {etime:>5s}",
        )
        for line in output:
            print(line)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        host = socket.gethostname().split('.')[0].lower()
        print(
            f'\nMyQS {options.get_release()}, '
            f'My Queuing System batch job statistics on HOST "{host}".\n',
        )
        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine home directory.",
            )
        self._myqsdir = Path(Path.home(), '.config', 'myqs', host)
        self._showjobs()
        self._myqsd()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
