#!/usr/bin/env python3
"""
Calculate PAR2 parity and repair tool.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

IGNORE_EXTENSION = ('.fsum', '.md5', '.md5sum', '.par2')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_check_flag(self):
        """
        Return check flag.
        """
        return self._args.check_flag

    def get_files(self):
        """
        Return list of file.
        """
        return self._args.files

    def get_par2(self):
        """
        Return par2 Command class object.
        """
        return self._par2

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Parity and repair tool.')

        parser.add_argument(
            '-c',
            dest='check_flag',
            action='store_true',
            help='Check and repair files.'
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help='File or directory.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._par2 = command_mod.Command('par2', errors='stop')

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

    @classmethod
    def _create(cls, cmdline, file):
        if os.path.isdir(file):
            for file2 in sorted(
                    glob.glob(os.path.join(file, '..*.par2')) +
                    glob.glob(os.path.join(file, '*'))
            ):
                cls._create(cmdline, file2)
        elif os.path.isfile(file):
            directory, name = os.path.split(file)
            root, ext = os.path.splitext(name)
            if ext in IGNORE_EXTENSION:
                if ext == '.par2'and root.startswith('..'):
                    if not os.path.isfile(os.path.join(directory, root[2:])):
                        print('\nDeleting old:', file)
                        try:
                            os.remove(file)
                        except OSError:
                            pass
                return

            file_time = os.path.getmtime(file)
            par_file = os.path.join(directory, '..{0}.par2'.format(name))
            if (
                    not os.path.isfile(par_file) or
                    file_time != os.path.getmtime(par_file)
            ):
                size = os.path.getsize(file) // 400 * 4 + 4
                task = subtask_mod.Task(cmdline + [
                    '-s'+str(size),
                    '-a'+par_file,
                    file
                ])
                task.run(pattern='^$', replace=(
                    'Opening: ',
                    'Opening: {0:s}{1:s}'.format(directory, os.sep)
                ))
                if task.get_exitcode() == 0:
                    try:
                        shutil.move(os.path.join(
                            directory,
                            '..{0:s}.vol0+1.par2'.format(name)
                        ), par_file)
                        os.utime(par_file, (file_time, file_time))
                    except OSError:
                        pass

    @classmethod
    def _repair(cls, cmdline, file):
        if os.path.isdir(file):
            for file2 in sorted(glob.glob(os.path.join(file, '*'))):
                cls._repair(cmdline, file2)
        elif os.path.isfile(file):
            directory, name = os.path.split(file)
            par_file = os.path.join(directory, '..{0}.par2'.format(name))
            if (
                    os.path.isfile(par_file) and
                    os.path.getmtime(file) == os.path.getmtime(par_file)
            ):
                task = subtask_mod.Task(cmdline + [par_file])
                task.run( pattern='^$|^Loading', replace=(
                    'Target: "',
                    'Target: {0:s}{1:s}'.format(directory, os.sep)
                ))

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        cmdline = options.get_par2().get_cmdline()
        if options.get_check_flag():
            cmdline.extend(['r', '-q'])
            for file in options.get_files():
                cls._repair(cmdline, file)
        else:
            cmdline.extend(['c', '-q', '-n1', '-r1'])
            for file in options.get_files():
                cls._create(cmdline, file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
