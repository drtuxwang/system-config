#!/usr/bin/env python3
"""
Converts file to '\r' newline format.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Converts file to "\\r" newline format.')

        parser.add_argument('files', nargs='+', metavar='file', help='File to change.')

        self._args = parser.parse_args(args)


class Fromdos:

    def __init__(self, options):
        for file in options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            print('Converting "' + file + '" file to "\\r" newline format...')
            try:
                with open(file, errors='replace') as ifile:
                    tmpfile = file + '-tmp' + str(os.getpid())
                    try:
                        with open(tmpfile, 'w', newline='\r') as ofile:
                            for line in ifile:
                                print(line.rstrip('\r\n'), file=ofile)
                    except IOError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' + tmpfile + '" file.')
                    except UnicodeDecodeError:
                        os.remove(tmpfile)
                        raise SystemExit(
                            sys.argv[0] + ': Cannot convert "' + file + '" binary file.')
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
            try:
                os.rename(tmpfile, file)
            except OSError:
                os.remove(tmpfile)
                raise SystemExit(sys.argv[0] + ': Cannot update "' + file + '" file.')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Fromdos(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
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
