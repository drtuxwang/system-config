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

BROWSER = 'firefox'
MAPPINGS = {
    'htm': BROWSER,
    'html': BROWSER,
    'xhtml': BROWSER,
    'mp3': 'audacity',
    'ogg': 'audacity',
    'wav': 'audacity',
    'ps': 'evince',
    'eps': 'evince',
    'pdf': 'evince',
    'gif': 'gimp',
    'jpeg': 'gimp',
    'jpg': 'gimp',
    'png': 'gimp',
    'doc': 'soffice',
    'docx': 'soffice',
    'odf': 'soffice',
    'odg': 'soffice',
    'ods': 'soffice',
    'odt': 'soffice',
    'ppt': 'soffice',
    'pptx': 'soffice',
    'wpd': 'soffice',
    'xls': 'soffice',
    'xlsx': 'soffice',
    'json': 'xedit',
    'txt': 'xedit'
}
URL_PREFIXS = ('http', 'https', 'ftp')


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
            elif prefix in URL_PREFIXS:
                self._spawn(BROWSER, file)
            elif not os.path.isfile(file):
                print(file + ': cannot find file.')
            else:
                command = MAPPINGS.get(extension)
                if command:
                    self._spawn(command, file)
                else:
                    print(file + ': unknown file extension.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
