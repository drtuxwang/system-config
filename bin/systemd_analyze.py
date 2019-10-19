#!/usr/bin/env python3
"""
Wrapper for "systemd-analyze" command
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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
    def _get_time(delays):
        """
        Convert delay to seconds.
        """
        seconds = 0
        for delay in delays:
            if delay.endswith('min'):
                seconds += float(delay[:-3]) * 60
            elif delay.endswith('ms'):
                seconds += float(delay[:-2]) / 1000
            else:
                seconds += float(delay[:-1])

        return seconds

    @classmethod
    def _filter_run(cls, command):
        """
        Remove buggy firmware & loader timings.
        """
        task = subtask_mod.Batch(command.get_cmdline())
        task.run(error2output=True)
        for line in task.get_output():
            if line.startswith('Startup finished in '):
                timings = []
                boot_time = 0
                for timing in line.split(
                        'Startup finished in '
                )[-1].split(' = ')[0].split(' + '):
                    *delays, name = timing.split()
                    if name not in ('(firmware)', '(loader)'):
                        timings.append(timing)
                        boot_time += cls._get_time(delays)
                print("Startup finished in {0:s} = {1:5.3f}s".format(
                    ' + '.join(timings),
                    boot_time
                ))
            else:
                print(line)

    @classmethod
    def run(cls):
        """
        Start program
        """
        command = command_mod.Command(
            '/usr/bin/systemd-analyze',
            args=sys.argv[1:],
            errors='stop'
        )
        if sys.argv[1:] not in ([], ['time']):
            subtask_mod.Exec(command.get_cmdline()).run()
        cls._filter_run(command)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
