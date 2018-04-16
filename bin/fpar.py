#!/usr/bin/env python3
"""
Calculate PAR2 parity and repair tool.
"""

import argparse
import glob
import logging
import os
import shutil
import signal
import sys

import command_mod
import logging_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

IGNORE_EXTENSIONS = ('.fsum', '.md5', '.md5sum', '.par2')

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable=invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

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
        self._par2.set_args(['c', '-q', '-n1', '-r1'])

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

    @staticmethod
    def _create_3dot_directory(directory):
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "{0:s}" directory.'.format(
                        directory))

    @staticmethod
    def _delete_file(file):
        try:
            os.remove(file)
        except OSError:
            pass

    @classmethod
    def _check_3dot_directory(cls, directory):
        if os.path.isdir(directory):
            for par_file in sorted(os.listdir(directory)):
                if par_file.endswith('.par2'):
                    file = os.path.join(directory, os.pardir, par_file[:-5])
                    if os.path.isfile(file):
                        continue
                    file = os.path.join(directory, par_file)
                    logger.warning("Deleting old: %s", file)
                    cls._delete_file(file)
            if not os.listdir(directory):
                os.removedirs(directory)

    @classmethod
    def _update(cls, cmdline, files):
        for file in sorted(files):
            directory, name = os.path.split(file)
            if not directory:
                directory = os.curdir
            if os.path.isdir(file):
                cls._check_3dot_directory(os.path.join(file, '...'))
                cls._update(cmdline, glob.glob(os.path.join(file, '*')))
            elif (
                    os.path.isfile(file) and
                    not os.path.islink(file) and
                    os.path.getsize(file)
            ):
                fpar_directory = os.path.join(directory, '...')
                cls._create_3dot_directory(fpar_directory)

                if name.endswith(IGNORE_EXTENSIONS):
                    continue

                file_time = os.path.getmtime(file)
                par_file = os.path.join(directory, '...', name+'.par2')
                if (
                        not os.path.isfile(par_file) or
                        file_time != os.path.getmtime(par_file)
                ):
                    tmpfile = os.path.join(directory, '....par2')
                    size = os.path.getsize(file) // 400 * 4 + 4
                    task = subtask_mod.Task(
                        cmdline + ['-s'+str(size), tmpfile, file]
                    )
                    task.run(pattern='^$', replace=(
                        'Opening: ',
                        'Opening: {0:s}{1:s}'.format(directory, os.sep)
                    ))
                    if task.get_exitcode() == 0:
                        cls._delete_file(tmpfile)
                        try:
                            shutil.move(
                                os.path.join(directory, '....vol0+1.par2'),
                                par_file
                            )
                            os.utime(par_file, (file_time, file_time))
                        except OSError:
                            pass

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        cmdline = options.get_par2().get_cmdline()
        cls._update(cmdline, options.get_files())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
