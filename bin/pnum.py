#!/usr/bin/env python3
"""
Renumber picture files into a numerical series.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

import file_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

IMAGE_EXTS = {'bmp', 'gif', 'jpeg', 'jpg', 'pcx', 'png', 'svg', 'tif', 'tiff'}


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def get_order(self):
        """
        Return order method.
        """
        return self._args.order

    def get_reset_flag(self):
        """
        Return per directory number reset flag
        """
        return self._args.reset_flag

    def get_start(self):
        """
        Return start number.
        """
        return self._args.start[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Renumber picture files into a numerical series.')

        parser.add_argument(
            '-ctime',
            action='store_const',
            const='ctime',
            dest='order',
            default='file',
            help='Sort using meta data change time.'
        )
        parser.add_argument(
            '-mtime',
            action='store_const',
            const='mtime',
            dest='order',
            default='file',
            help='Sort using modification time.'
        )
        parser.add_argument(
            '-noreset',
            dest='reset_flag',
            action='store_false',
            help='Use same number sequence for all directories.'
        )
        parser.add_argument(
            '-start',
            nargs=1,
            type=int,
            default=[1],
            help='Select number to start from.'
        )
        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help='Directory containing picture files.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Picture directory "' + directory +
                    '" does not exist.'
                )


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
    def _sorted(options, file_stats):
        order = options.get_order()
        if order == 'mtime':
            file_stats = sorted(file_stats, key=lambda s: s.get_time())
        elif order == 'ctime':
            file_stats = sorted(file_stats, key=lambda s: s.get_time_change())
        else:
            file_stats = sorted(file_stats, key=lambda s: s.get_file())
        return file_stats

    def run(self):
        """
        Start program
        """
        options = Options()

        startdir = os.getcwd()
        reset_flag = options.get_reset_flag()
        number = options.get_start()

        for directory in options.get_directories():
            if reset_flag:
                number = options.get_start()
            if os.path.isdir(directory):
                os.chdir(directory)
                file_stats = []
                for file in glob.glob('*.*'):
                    if file.split('.')[-1].lower() in IMAGE_EXTS:
                        file_stats.append(file_mod.FileStat(file))
                newfiles = []
                mypid = os.getpid()
                for file_stat in self._sorted(options, file_stats):
                    newfile = 'pic{0:05d}.{1:s}'.format(
                        number,
                        file_stat.get_file().split('.')[-1].lower(
                            ).replace('jpeg', 'jpg'))
                    newfiles.append(newfile)
                    try:
                        shutil.move(
                            file_stat.get_file(),
                            str(mypid) + '-' + newfile
                        )
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot rename "' +
                            file_stat.get_file() + '" image file.'
                        )
                    number += 1
                for file in newfiles:
                    try:
                        shutil.move(str(mypid) + '-' + file, file)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot rename to "' + file +
                            '" image file.'
                        )
                os.chdir(startdir)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
