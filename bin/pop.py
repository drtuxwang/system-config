#!/usr/bin/env python3
"""
Send popup message to display.
"""

import argparse
import glob
import os
import signal
import sys
import time
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_run_flag(self) -> bool:
        """
        Return run flag.
        """
        return self._args.run

    def get_time_delay(self) -> int:
        """
        Return time delay in minutes.
        """
        return self._args.timeDelay[0]

    def get_words(self) -> List[str]:
        """
        Return words.
        """
        return self._args.words

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Send popup message to display.",
        )

        parser.add_argument(
            '-run',
            action='store_true',
            dest='run',
            help="Run command and notify on completion.",
        )
        parser.add_argument(
            '-time',
            nargs=1,
            type=int,
            dest='timeDelay',
            default=[0],
            help="Delay popup in minutes.",
        )
        parser.add_argument(
            'words',
            nargs='+',
            metavar='word',
            help="A word.",
        )

        if args[0:1] == ['-run']:
            args = [args[0], '--'] + args[1:]
        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.timeDelay[0] < 0:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                'positive integer for delay time.',
            )


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
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def notify(options: Options) -> int:
        """
        Send notify message.
        """
        args = options.get_words()
        exitcode = 0

        if options.get_run_flag():
            start_time = time.time()
            command = command_mod.Command(args[0], errors='ignore')
            if command.is_found():
                command.set_args(args[1:])
                task = subtask_mod.Task(command.get_cmdline())
                task.run()
                exitcode = task.get_exitcode()

                args = [' '.join(args)]
                if exitcode:
                    args.append('has failed')
                else:
                    args.append('has completed')
            else:
                args = args[:1] + ['not found']
                exitcode = 1
            elapsed_time = time.time() - start_time
            print(f"Elapsed time (s): {elapsed_time:5.3f} ")
        else:
            args = [' '.join(args)]

        delay = 60 * options.get_time_delay()
        time.sleep(delay)

        bell = command_mod.Command('bell', errors='ignore')
        if bell.is_found():
            subtask_mod.Background(bell.get_cmdline()).run()

        pop = command_mod.Command('notify-send', errors='stop')
        pop.set_args(['--expire-time=30', '--'] + args)
        task = subtask_mod.Task(pop.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )

        raise SystemExit(exitcode)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        cls.notify(options)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
