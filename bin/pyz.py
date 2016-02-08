#!/usr/bin/env python3
"""
Make a Python3 ZIP Application in PYZ format.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Make a Python3 ZIP Application in PYZ format.')

        parser.add_argument('archive', nargs=1, metavar='file.pyz', help='Archive file.')
        parser.add_argument('files', nargs='*', metavar='file', help='File to archive.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.name == 'nt':
            self._archiver = syslib.Command('pkzip32.exe', check=False)
            if self._archiver.is_found():
                self._archiver.set_flags(
                    ['-add', '-maximum', '-recurse', '-path', self._args.archive[0] + '-zip'])
            else:
                self._archiver = syslib.Command(
                    'zip', flags=['-r', '-9', self._args.archive[0] + '-zip'])
        else:
            self._archiver = syslib.Command(
                'zip', flags=['-r', '-9', self._args.archive[0] + '-zip'])

        if self._args.files:
            self._archiver.set_args(self._args.files)
        else:
            self._archiver.set_args(os.listdir())

        if '__main__.py' not in self._archiver.get_args():
            raise SystemExit(sys.argv[0] + ': Cannot find "__main__.py" main program file.')

    def get_archive(self):
        """
        Return archive location.
        """
        return self._args.archive


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

    def _make_pyz(self, archive):
        try:
            with open(archive, 'wb') as ofile:
                ofile.write(b'#!/usr/bin/env python3\n')
                with open(archive + '-zip', 'rb') as ifile:
                    self._copy(ifile, ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + archive + '" Python3 ZIP Application.')
        try:
            os.remove(archive + '-zip')
        except OSError:
            pass
        os.chmod(archive, int('755', 8))

    @staticmethod
    def _copy(ifile, ofile):
        while True:
            chunk = ifile.read(131072)
            if not chunk:
                break
            ofile.write(chunk)

    def run(self):
        """
        Start program
        """
        options = Options()
        archiver = options.get_archiver()

        archiver.run()
        if archiver.get_exitcode():
            print(
                sys.argv[0] + ': Error code ' + str(archiver.get_exitcode()) + ' received from "' +
                archiver.get_file() + '".', file=sys.stderr)
            raise SystemExit(archiver.get_exitcode())
        self._make_pyz(options.get_archive())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
