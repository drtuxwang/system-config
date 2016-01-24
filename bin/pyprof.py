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

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

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
        parser = argparse.ArgumentParser(description='Profile Python 3.x program.')

        parser.add_argument('-n', nargs=1, type=int, dest='lines', default=[20],
                            metavar='K', help='Output first K lines.')

        parser.add_argument('file', nargs=1, metavar='file[.py]|file.pstats',
                            help='Python module or pstats file.')

        my_args = []
        while len(args):
            my_args.append(args[0])
            if not args[0].startswith('-'):
                break
            elif args[0] == '-n' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(my_args)

        self._module_args = args[1:]


class Profiler(object):
    """
    Profiler class
    """

    def __init__(self, options):
        self._options = options

    def _profile(self, module_file, module_args):
        stats_file = os.path.basename(module_file.rsplit('.', 1)[0] + '.pstats')
        if os.path.isfile(stats_file):
            try:
                os.remove(stats_file)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot remove old "' + stats_file + '" file.')

        python3 = syslib.Command(file=sys.executable)
        python3.set_args(['-m', 'cProfile', '-o', stats_file])

        if os.path.isfile(module_file):
            command = syslib.Command(file=module_file)
        else:
            try:
                command = syslib.Command(module_file)
            except syslib.SyslibError:
                raise SystemExit(sys.argv[0] + ': Cannot find "' + module_file + '" module file')
        command.set_args(module_args)
        command.set_wrapper(python3)
        command.run()

        print('pyprof:', command.args2cmd([command.get_file()] + module_args))
        return stats_file

    def _show(self, stats_file, lines):
        try:
            stats = pstats.Stats(stats_file)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + stats_file + '" file.')

        stats.strip_dirs().sort_stats('tottime', 'cumtime').print_stats(lines)

    def run(self):
        """
        Start profiling
        """
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


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Profiler(options).run()
        except KeyboardInterrupt:
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
