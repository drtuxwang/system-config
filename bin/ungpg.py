#!/usr/bin/env python3
"""
Unpack an encrypted archive in gpg (pgp compatible) format.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_gpg(self):
        """
        Return gpg Command class object.
        """
        return self._gpg

    @staticmethod
    def _config():
        if 'HOME' in os.environ:
            os.umask(int('077', 8))
            gpgdir = os.path.join(os.environ['HOME'], '.gnupg')
            if not os.path.isdir(gpgdir):
                try:
                    os.mkdir(gpgdir)
                except OSError:
                    return
            try:
                os.chmod(gpgdir, int('700', 8))
            except OSError:
                return
        if 'DISPLAY' in os.environ:
            os.environ['DISPLAY'] = ''

    @staticmethod
    def _set_libraries(command):
        libdir = os.path.join(os.path.dirname(command.get_file()), 'lib')
        if os.path.isdir(libdir) and os.name == 'posix':
            if os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        libdir + os.pathsep + os.environ['LD_LIBRARY_PATH'])
                else:
                    os.environ['LD_LIBRARY_PATH'] = libdir

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack an encrypted archive in gpg '
            '(pgp compatible) format.'
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.gpg|file.pgp',
            help='GPG/PGP encrypted file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._gpg = command_mod.Command('gpg', errors='stop')

        self._config()
        self._set_libraries(self._gpg)


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

        gpg = options.get_gpg()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            gpg.set_args([file])
            task = subtask_mod.Task(gpg.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
