#!/usr/bin/env python3
"""
Wrapper for "watch" command

Enables "q" to quit
"""

import os
import signal
import sys
import termios
import threading
import types
from pathlib import Path

import readchar  # type: ignore

from command_mod import Command
from subtask_mod import Task


class EventThread(threading.Thread):
    """
    This class monitor keyboard and quit when q key is pressed
    """

    def __init__(self) -> None:
        super().__init__()
        self.exit_event = threading.Event()

    def stop(self) -> None:
        """
        Signal thread to stop
        """
        self.exit_event.set()

    def run(self) -> None:
        try:
            while not self.exit_event.is_set():
                if readchar.readkey() == 'q':
                    self.exit_event.set()
                    os.killpg(os.getpid(), signal.SIGTERM)
        except KeyboardInterrupt:
            os.killpg(os.getpid(), signal.SIGTERM)
            self.exit_event.set()


class Watch:
    """
    This class runs "watch" command and add ability to quit using "q" key
    """
    def __init__(self, command: Command) -> None:
        mypid = os.getpid()
        os.setpgid(mypid, mypid)
        self._command = command
        self._thread = EventThread()
        self._ttycfg = termios.tcgetattr(sys.stdin.fileno())
        signal.signal(signal.SIGTERM, self._sigterm)

    def cleanup(self) -> None:
        """
        Clean up multiple threading
        """
        self._thread.stop()
        self._thread.join()
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, self._ttycfg)

    def _sigterm(self, _signum: int, _frame: types.FrameType) -> None:
        self.cleanup()
        sys.exit(4)

    def run(self) -> None:
        """
        Run command
        """
        try:
            self._thread.start()
            Task(self._command.get_cmdline()).run()
        except (EOFError, KeyboardInterrupt):
            self.cleanup()
            sys.exit(114)
        self.cleanup()


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

    def run(self) -> int:
        """
        Start program
        """
        command = Command('watch', args=sys.argv[1:], errors='stop')
        if not sys.argv[1:] or len(set(sys.argv[1:]) & set(
            ('-h', '-help', '--help')
        )):
            Task(command.get_cmdline()).run()
        else:
            Watch(command).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
