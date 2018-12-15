#!/usr/bin/env python3
"""
Send text/images/postscript/PDF files to browser for printing.
"""

import argparse
import getpass
import glob
import os
import shutil
import signal
import sys
import time

import command_mod
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

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Send files to browser for printing.'
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='A text/images/postscript/PDF file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
        sys.exit(0)

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
    def _print(files):
        os.umask(int('077', 8))
        tmpdir = "/tmp/{0:s}/fprint".format(getpass.getuser())
        if not os.path.isdir(tmpdir):
            os.makedirs(tmpdir)
        pdf = command_mod.Command('pdf', errors='stop')
        xweb = command_mod.Command('xweb', errors='stop')

        for number, file in enumerate(files):
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')

            tmpfile = "{0:s}/{1:02d}.pdf".format(tmpdir, number)
            task = subtask_mod.Batch(pdf.get_cmdline() + [tmpfile, file])
            task.run()
            if task.get_exitcode():
                raise SystemExit("{0:s}: Cannot convert to PDF: {1:s}".format(
                    sys.argv[0],
                    file,
                ))

            print("Sending to browser for printing: {0:s}".format(file))
            task = subtask_mod.Daemon(xweb.get_cmdline() + [tmpfile])
            task.run()
            time.sleep(0.5)

        time.sleep(2)
        shutil.rmtree(tmpdir)

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()
        cls._print(options.get_files())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
