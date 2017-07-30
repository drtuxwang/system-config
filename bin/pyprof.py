#!/usr/bin/env python3
"""
Profile Python 3.x program.
"""

import argparse
import glob
import os
import pstats
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._module_args = None
        self.parse(sys.argv)

    def get_file(self):
        """
        Return list of file.
        """
        return self._args.file[0]

    def get_module_args(self):
        """
        Return module args.
        """
        return self._module_args

    def get_lines(self):
        """
        Return number of lines.
        """
        return self._args.lines[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Profile Python 3.x program.')

        parser.add_argument(
            '-n',
            nargs=1,
            type=int,
            dest='lines',
            default=[20],
            metavar='K',
            help='Output first K lines.'
        )
        parser.add_argument(
            'file',
            nargs=1,
            metavar='file[.py]|file.pstats',
            help='Python module or pstats file.'
        )

        my_args = []
        while args:
            my_args.append(args[0])
            if not args[0].startswith('-'):
                break
            elif args[0] == '-n' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(my_args)

        self._module_args = args[1:]

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main(object):
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
    def _get_command(module_file, module_args):
        if os.path.isfile(module_file):
            return command_mod.CommandFile(module_file, args=module_args)

        try:
            return command_mod.Command(module_file, args=module_args)
        except command_mod.CommandNotFoundError:
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + module_file +
                '" module file'
            )

    @classmethod
    def _profile(cls, module_file, module_args):
        stats_file = os.path.basename(
            module_file.rsplit('.', 1)[0] + '.pstats')
        if os.path.isfile(stats_file):
            try:
                os.remove(stats_file)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot remove old "' +
                    stats_file + '" file.'
                )

        python3 = command_mod.CommandFile(sys.executable)
        python3.set_args(['-B', '-m', 'cProfile', '-o', stats_file])

        command = cls._get_command(module_file, module_args)

        task = subtask_mod.Task(python3.get_cmdline() + command.get_cmdline())
        task.run()

        print("pyprof:", command.args2cmd([command.get_file()] + module_args))
        return stats_file

    @staticmethod
    def _show(stats_file, lines):
        try:
            stats = pstats.Stats(stats_file)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + stats_file + '" file.')

        stats.strip_dirs().sort_stats('tottime', 'cumtime').print_stats(lines)

    def run(self):
        """
        Start program
        """
        self._options = Options()
        file = self._options.get_file()

        if not file.endswith('.pstats'):
            if not file.endswith('.py'):
                file = file + '.py'
            file = self._profile(file, self._options.get_module_args())

        self._show(file, self._options.get_lines())

        file = self._options.get_file()

        if not file.endswith('.pstats'):
            if not file.endswith('.py'):
                file = file + '.py'
            file = self._profile(file, self._options.get_module_args())

        self._show(file, self._options.get_lines())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
