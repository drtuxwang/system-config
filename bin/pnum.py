#!/usr/bin/env python3
"""
Renumber picture files into a numerical series.
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

    def getDirectories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def getOrder(self):
        """
        Return order method.
        """
        return self._args.order

    def getResetFlag(self):
        """
        Return per directory number reset flag
        """
        return self._args.resetFlag

    def getStart(self):
        """
        Return start number.
        """
        return self._args.start[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Renumber picture files into a numerical series.')

        parser.add_argument('-ctime', action='store_const', const='ctime', dest='order',
                            default='file', help='Sort using file creation time.')
        parser.add_argument('-mtime', action='store_const', const='mtime', dest='order',
                            default='file', help='Sort using file modification time.')
        parser.add_argument('-noreset', dest='resetFlag', action='store_false',
                            help='Use same number sequence for all directories.')
        parser.add_argument('-start', nargs=1, type=int, default=[1],
                            help='Select number to start from.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory containing picture files.')

        self._args = parser.parse_args(args)

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Picture directory "' + directory + '" does not exist.')


class Renumber:

    def __init__(self, options):
        startdir = os.getcwd()
        resetFlag = options.getResetFlag()
        number = options.getStart()

        for directory in options.getDirectories():
            if resetFlag:
                number = options.getStart()
            if os.path.isdir(directory):
                os.chdir(directory)
                fileStats = []
                for file in glob.glob('*.*'):
                    if (file.split('.')[-1].lower() in (
                            'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pcx', 'svg', 'tif', 'tiff')):
                        fileStats.append(syslib.FileStat(file))
                newfiles = []
                mypid = os.getpid()
                for fileStat in self._sorted(options, fileStats):
                    newfile = 'pic{0:05d}.{1:s}'.format(
                        number, fileStat.getFile().split('.')[-1].lower().replace('jpeg', 'jpg'))
                    newfiles.append(newfile)
                    try:
                        os.rename(fileStat.getFile(), str(mypid) + '-' + newfile)
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot rename "' + fileStat.getFile() +
                                         '" image file.')
                    number += 1
                for file in newfiles:
                    try:
                        os.rename(str(mypid) + '-' + file, file)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot rename to "' + file + '" image file.')
                os.chdir(startdir)

    def _sorted(self, options, fileStats):
        order = options.getOrder()
        if order == 'mtime':
            fileStats = sorted(fileStats, key=lambda s: s.getTime())
        elif order == 'ctime':
            fileStats = sorted(fileStats, key=lambda s: s.getTimeCreate())
        else:
            fileStats = sorted(fileStats, key=lambda s: s.getFile())
        return fileStats


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Renumber(options)
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
