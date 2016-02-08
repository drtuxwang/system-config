#!/usr/bin/env python3
"""
Run CLAMAV anti-virus scanner.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_lamscan(self):
        """
        Return clamscan Command class object.
        """
        return self._clamscan

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Run ClamAV anti-virus scanner.')

        parser.add_argument('files', nargs='+', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._clamscan = syslib.Command('clamscan')
        self._clamscan.set_flags(['-r'])
        self._clamscan.set_args(self._args.files)


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
    def run():
        """
        Start program
        """
        options = Options()
        clamscan = options.get_lamscan()

        clamscan.run()
        print('---------- VIRUS DATABASE ----------')
        if os.name == 'nt':
            os.chdir(os.path.join(os.path.dirname(clamscan.get_file())))
            directory = 'database'
        elif os.path.isdir('/var/clamav'):
            directory = '/var/clamav'
        else:
            directory = '/var/lib/clamav'
        for file in sorted(glob.glob(os.path.join(directory, '*c[lv]d'))):
            file_stat = syslib.FileStat(file)
            print('{0:10d} [{1:s}] {2:s}'.format(
                file_stat.get_size(), file_stat.get_time_local(), file))

        return clamscan.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
