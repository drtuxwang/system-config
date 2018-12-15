#!/usr/bin/env python3
"""
Resize large picture images to mega-pixels limit.
"""

import argparse
import glob
import math
import os
import signal
import sys

import command_mod
import config_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_convert(self):
        """
        Return convert Command class object.
        """
        return self._convert

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def get_megs(self):
        """
        Return mega-pixels.
        """
        return self._args.megs[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Resize large picture images to mega-pixels limit.')

        parser.add_argument('-megs', nargs=1, type=float, default=[9],
                            help='Select mega-pixels. Default is 9.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory containing JPEG files to resize.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._convert = command_mod.Command('convert', errors='stop')

        if self._args.megs[0] < 1:
            raise SystemExit(
                sys.argv[0] +
                ': You must specific a positive number for megabytes.'
            )

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Image directory "' + directory +
                    '" does not exist.'
                )


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

    def _imagesize(self, file):
        self._convert.set_args(['-verbose', file, '/dev/null'])
        task = subtask_mod.Batch(self._convert.get_cmdline())
        task.run(pattern='^' + file + '=>', error2output=True)
        if not task.has_output():
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" picture file.')
        elif task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )
        x_size, y_size = task.get_output(
            )[0].split('+')[0].split()[-1].split('x')
        return int(x_size), int(y_size)

    def run(self):
        """
        Start program
        """
        options = Options()
        self._convert = options.get_convert()
        megs = options.get_megs()
        images_extensions = config_mod.Config().get('image_extensions')

        for directory in options.get_directories():
            for file in sorted(glob.glob(os.path.join(directory, '*'))):
                if os.path.splitext(file)[1].lower() in images_extensions:
                    ix_size, iy_size = self._imagesize(file)
                    imegs = ix_size * iy_size / 1000000
                    print("{0:s}: {1:d} x {2:d} ({3:4.2f})".format(
                        file, ix_size, iy_size, imegs), end='')
                    resize = math.sqrt(megs / imegs)
                    ox_size = int(ix_size*resize + 0.5)
                    oy_size = int(iy_size*resize + 0.5)
                    if ox_size < ix_size and oy_size < iy_size:
                        print(" => {0:d} x {1:d} ({2:4.2f})".format(
                            ox_size,
                            oy_size,
                            ox_size * oy_size / 1000000
                        ), end='')
                        self._convert.set_args([
                            '-verbose',
                            '-size',
                            str(ox_size) + 'x' + str(oy_size),
                            '-resize',
                            str(ox_size) + 'x' + str(oy_size) + '!',
                            file, file
                        ])
                        task = subtask_mod.Batch(self._convert.get_cmdline())
                        task.run()
                        if task.get_exitcode():
                            raise SystemExit(
                                sys.argv[0] + ': Error code ' +
                                str(task.get_exitcode()) + ' received from "' +
                                task.get_file() + '".'
                            )
                    print()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
