#!/usr/bin/env python3
"""
Open files using default application.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


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

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Open files using default application.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File to open.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
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
    def _spawn(program, file):
        print(file + ': opening with "' + program + '"...')
        program = command_mod.Command(program, args=[file], errors='stop')
        subtask_mod.Daemon(program.get_cmdline()).run()

    def run(self):
        """
        Start program
        """
        options = Options()

        files = options.get_files()

        for file in files:
            prefix = file.split(':', 1)[0]
            extension = file.rsplit('.', 1)[-1].lower()

            if os.path.isdir(file):
                self._spawn('xdesktop', file)
            elif prefix in ('http', 'https', 'ftp'):
                self._spawn('firefox', file)
            elif not os.path.isfile(file):
                print(file + ': cannot find file.')
            elif extension in ('mp3', 'ogg', 'wav'):
                self._spawn('audacity', file)
            elif extension in ('eps', 'ps', 'pdf'):
                self._spawn('evince', file)
            elif extension in ('htm', 'html', 'xhtml'):
                self._spawn('firefox', file)
            elif extension in ('jpg', 'jpeg', 'png'):
                self._spawn('gimp', file)
            elif extension in (
                    'doc', 'docx', 'odf', 'odg', 'ods', 'odt', 'ppt',
                    'pptx', 'wpd', 'xls', 'xlsx'
            ):
                self._spawn('soffice', file)
            elif extension in ('txt', 'json'):
                self._spawn('xedit', file)
            else:
                print(file + ': unknown file extension.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
