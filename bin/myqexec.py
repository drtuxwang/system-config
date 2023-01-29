#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job execution.
"""

import os
import signal
import socket
import sys
import time
from pathlib import Path
from typing import List

import command_mod
import subtask_mod

RELEASE = '2.8.6'


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._release = RELEASE
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

    def get_release(self) -> str:
        """
        Return release version.
        """
        return self._release

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
    def _get_command(file: str) -> command_mod.Command:
        if Path(file).is_file():
            return command_mod.CommandFile(Path(file).resolve())
        return command_mod.Command(file, errors='stop')

    def _spawn(self, options: Options) -> None:
        path = Path(self._myqsdir, f'{self._jobid}.r')
        try:
            with path.open('a') as ofile:
                mypid = os.getpid()
                os.setpgid(mypid, mypid)  # New PGID
                pgid = os.getpgid(mypid)
                print(f"PGID={pgid}\nSTART={time.time()}", file=ofile)
        except OSError:
            return

        try:
            with path.open(errors='replace') as ifile:
                info = {}
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        info[line.split('=')[0]] = line.split('=', 1)[1]
        except OSError:
            return

        print(
            f"\nMyQS v{options.get_release()}, "
            "My Queuing System batch job exec.\n",
        )
        print("MyQS JOBID  =", self._jobid)
        print("MyQS QUEUE  =", info['QUEUE'])
        print("MyQS NCPUS  =", info['NCPUS'])
        print("MyQS PGID   =", pgid)
        print("MyQS START  =", time.strftime('%Y-%m-%d-%H:%M:%S'))
        print("-"*80)
        sys.stdout.flush()
        os.environ['PATH'] = info['PATH']
        command = self._get_command(info['COMMAND'])
        self._sh(command)
        subtask_mod.Exec(command.get_cmdline()).run()

    @staticmethod
    def _sh(command: command_mod.Command) -> None:
        try:
            with Path(command.get_file()).open(errors='replace') as ifile:
                line = ifile.readline().rstrip()
                if line == '#!/bin/sh':
                    command.set_args(['/bin/sh'] + command.get_cmdline())
        except OSError:
            pass

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
        renice = command_mod.Command('renice', errors='ignore')
        if renice.is_found():
            renice.set_args(['100', os.getpid()])
            subtask_mod.Batch(renice.get_cmdline()).run()
        myqexec = command_mod.CommandFile(
            __file__,
            args=['-spawn', self._jobid]
        )
        subtask_mod.Task(myqexec.get_cmdline()).run()
        print("-"*80)
        print("MyQS FINISH =", time.strftime('%Y-%m-%d-%H:%M:%S'))
        time.sleep(1)
        try:
            path.unlink()
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
            self._spawn(options)
        else:
            self._start()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
