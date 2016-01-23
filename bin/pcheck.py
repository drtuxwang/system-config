#!/usr/bin/env python3
"""
Check JPEG picture files.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Check JPEG picture files.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory containing JPEG files to check.')

        self._args = parser.parse_args(args)


class Check(object):
    """
    Check class
    """

    def __init__(self, options):
        self._directories = options.get_directories()

    def run(self):
        """
        Start checking
        """
        errors = []
        jpeginfo = syslib.Command('jpeginfo', flags=['--info', '--check'])
        for directory in self._directories:
            if os.path.isdir(directory):
                files = []
                for file in glob.glob(os.path.join(directory, '*.*')):
                    if file.split('.')[-1].lower() in ('jpg', 'jpeg'):
                        files.append(file)
                if files:
                    jpeginfo.set_args(files)
                    jpeginfo.run(mode='batch')
                    for line in jpeginfo.get_output():
                        if '[ERROR]' in line:
                            errors.append(line)
                        else:
                            print(line)
        if errors:
            for line in errors:
                print(line)
            raise SystemExit('Total errors encountered: ' + str(len(errors)) + '.')


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
            Check(options).run()
        except (EOFError, KeyboardInterrupt):
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
