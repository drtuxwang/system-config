#!/usr/bin/env python3
"""
Wrapper for "systemd-analyze" command
"""

import re
import signal
import sys
from typing import Generator

from command_mod import Command
from subtask_mod import Batch, Exec


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

    @staticmethod
    def _get_timings(line: str) -> Generator[tuple, None, None]:
        """
        Return (delay, name) timings
        """
        isjunk = re.compile(r'^Startup finished in |\(|\)| =.*')
        for timing in isjunk.sub('', line).split(' + '):
            delay, name = timing.split(' ', 1)
            if delay.endswith('min'):
                seconds = float(delay[:-3]) * 60.
            elif delay.endswith('ms'):
                seconds = float(delay[:-2]) / 1000.
            else:
                seconds = float(delay[:-1])
            yield seconds, name

    @classmethod
    def _filter_run(cls, command: Command) -> None:
        """
        Remove buggy firmware & loader timings.
        """
        task = Batch(command.get_cmdline())
        task.run(error2output=True)
        for line in task.get_output():
            if line.startswith('Startup finished in '):
                timings = []
                boot_time = 0.
                for seconds, name in cls._get_timings(line):
                    timings.append(f"{seconds:5.3f}s ({name})")
                    boot_time += seconds
                print(
                    f"Startup finished in {' + '.join(timings)} = "
                    f"{boot_time:5.3f}s",
                )
            else:
                print(line)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        command = Command(
            '/usr/bin/systemd-analyze',
            args=sys.argv[1:],
            errors='stop'
        )
        if sys.argv[1:] not in ([], ['time']):
            Exec(command.get_cmdline()).run()
        cls._filter_run(command)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
