#!/usr/bin/env python3
"""
Normalize volume of wave files to 8 dB.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._normalize = syslib.Command('normalize-audio', check=False)
        if not self._normalize.isFound():
            self._normalize = syslib.Command('normalize')

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getNormalize(self):
        """
        Return normalize Command class object.
        """
        return self._normalize

    def getViewFlag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Normalize volume of wave files to 8 dB.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='View volume only.')

        parser.add_argument('files', nargs='+', metavar='file.wav', help='Audio file.')

        self._args = parser.parse_args(args)


class Normalize:

    def __init__(self, options):
        self._options = options
        self._normalize = options.getNormalize()

        for file in options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            elif file[-4:] != '.wav':
                raise SystemExit(sys.argv[0] + ': Cannot handle "' + file + '" non-wave file.')
            volume, pvolume = self._view(file)
            sys.stdout.write(file + ': ' + volume.rjust(8) +
                             ' dB (' + pvolume.rjust(8) + ' dB peak)')
            if not options.getViewFlag():
                for npass in range(4):
                    self._adjust(file)
                    sys.stdout.write(' ' + str(npass) + '>>')
                    volume, pvolume = self._view(file)
                    sys.stdout.write(volume.rjust(8) + ' dB (' + pvolume.rjust(8) + ' dB peak)')
                    if volume.startswith('-8.'):
                        break
            print()

    def _adjust(self, file):
        self._normalize.setArgs(
            ['-q', '--amplitude=-8dBFS', '--adjust-threshold=0.00009dBFS', file])
        self._normalize.run(mode='batch')
        if self._normalize.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._normalize.getExitcode()) +
                             ' received from "' + self._normalize.getFile() + '".')

    def _view(self, file):
        self._normalize.setArgs(['-q', '--no-adjust', file])
        self._normalize.run(mode='batch')
        if (len(self._normalize.getOutput()) != 1 or
                len(self._normalize.getOutput()[0].split()) != 4):
            raise SystemExit(sys.argv[0] + ': Cannot read corrupt "' + file + '" wave file.')
        elif self._normalize.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._normalize.getExitcode()) +
                             ' received from "' + self._normalize.getFile() + '".')
        volume = self._normalize.getOutput()[0].split()[0].replace('dBFS', '')
        pvolume = self._normalize.getOutput()[0].split()[1].replace('dBFS', '')
        return (volume, pvolume)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Normalize(options)
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
