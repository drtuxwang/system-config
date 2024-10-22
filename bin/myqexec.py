#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job execution.
"""

import json
import os
import signal
import socket
import sys
import time
from pathlib import Path
from typing import List

from command_mod import Command, CommandFile
from subtask_mod import Batch, Exec, Task

RELEASE = '3.2.0'
VERSION = 20241021


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args = None
        self.parse(sys.argv)

    def get_jobid(self) -> str:
        """
        Return job ID.
        """
        return self._jobid

    def get_mode(self) -> str:
        """
        Return operation mode.
        """
        return self._mode

    def get_myqsdir(self) -> Path:
        """
        Return myqs directory.
        """
        return self._myqsdir

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        if len(args) != 3 or args[1] not in ('-jobid', '-spawn'):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot be started manually. '
                'Please run "myqsd" command.',
            )
        self._mode = args[1][1:]
        self._myqsdir = Path(
            Path.home(),
            '.config',
            'myqs',
            socket.gethostname().split('.')[0].lower()
        )
        self._jobid = args[2]


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

    @staticmethod
    def _get_command(command: str) -> Command:
        cmdline = Command.cmd2args(command)
        path = Path(cmdline[0])
        if path.is_file():
            return CommandFile(path.resolve(), args=cmdline[1:])
        return Command(path, errors='stop', args=cmdline[1:])

    def _spawn(self) -> None:
        mypid = os.getpid()
        os.setpgid(mypid, mypid)  # New PGID
        pgid = os.getpgid(mypid)
        if pgid != mypid:  # Double check new PGID
            return

        path = Path(self._myqsdir, f'{self._jobid}.r')
        try:
            with path.open('a') as ofile:
                print(f"START={time.time()}\nPGID={pgid}", file=ofile)
        except OSError:
            return

        info = self._get_info(path)
        nice = "nice -9" if info.get('QUEUE') == 'express' else "nice -18"
        command = self._get_command(info['COMMAND'])
        bash_command = command.args2cmd(command.get_cmdline())
        cmdline = [
            'bash',
            '-l',
            '-c',
            'trap - DEBUG;'
            'set -x; '
            f'time {nice} {bash_command}',
        ]
        print(f"\nMyQS v{RELEASE}, My Queuing System batch job exec.\n")
        print(f"MyQS JOBID       = {self._jobid}")
        print(f"MyQS QUEUE       = {info['QUEUE']}")
        print(f"MyQS NCPUS SLOTS = {info['NCPUS']}")
        print(f"MyQS DIRECTORY   = {info['DIRECTORY']}")
        print(f"MyQS COMMAND     = {info['COMMAND']}")
        print(f"MyQS START       = {time.strftime('%Y-%m-%dT%H:%M:%S%z')}")
        print(f"MyQS PGID        = {mypid}")
        print(f"MyQS EXECUTE     = {bash_command}")
        print("-"*80)
        sys.stdout.flush()
        os.environ['TIMEFORMAT'] = (
            ' [ time(s)  -  real: %2R  user: %2U  sys: %2S  cpu: %P%% ]'
        )
        Exec(cmdline).run()

    def _start(self) -> None:
        path = Path(self._myqsdir, f'{self._jobid}.r')
        try:
            with path.open(errors='replace') as ifile:
                info = {}
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        info[line.split('=')[0]] = line.split('=', 1)[1]
        except OSError:
            return
        if Path(info['DIRECTORY']).is_dir():
            os.chdir(info['DIRECTORY'])
        else:
            os.chdir(Path.home())

        myqexec = CommandFile(__file__, args=['-spawn', self._jobid])
        task = Task(myqexec.get_cmdline())
        task.run()

        myqstat = Command('myqstat', args=[self._jobid])
        task = Batch(myqstat.get_cmdline())
        task.run()
        output = json.dumps(task.get_output()[-2:], ensure_ascii=False)
        try:
            if task.get_exitcode():
                path_new = path.with_suffix('.f')
            else:
                path_new = path.with_suffix('.d')
            path.replace(path_new)
            with path_new.open('a') as ofile:
                print(f"FINISH={time.time()}", file=ofile)
                print(f"OUTPUT={output}", file=ofile)
        except OSError:
            pass

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._myqsdir = options.get_myqsdir()
        self._jobid = options.get_jobid()

        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine home directory.",
            )
        if options.get_mode() == 'spawn':
            self._spawn()
        else:
            self._start()

        return 0


if __name__ == '__main__':
    if sys.argv[-1] in ['-v', '-V', '-version', '--version']:
        print(f"MyQS {RELEASE} ({VERSION})")
    elif '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
