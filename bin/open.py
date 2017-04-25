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

BROWSER = 'chrome'
MAPPINGS = {
    '7z': 'un7z',
    'ace': 'unace',
    'bz2': 'unbz2',
    'csv': 'soffice',
    'deb': 'undeb',
    'dmg': 'undmg',
    'doc': 'soffice',
    'docx': 'soffice',
    'gpg': 'ungpg',
    'gif': 'gimp',
    'gz': 'ungz',
    'htm': BROWSER,
    'html': BROWSER,
    'iso': 'un7z',
    'jar': 'un7z',
    'jpeg': 'gimp',
    'jpg': 'gimp',
    'json': 'xedit',
    'mp3': 'audacity',
    'odf': 'soffice',
    'odg': 'soffice',
    'ods': 'soffice',
    'odt': 'soffice',
    'ogg': 'audacity',
    'png': 'gimp',
    'ppt': 'soffice',
    'pptx': 'soffice',
    'pdf': 'unpdf',
    'rar': 'un7z',
    'rpm': 'unrpm',
    'run': 'un7z',
    'sqlite': 'unsqlite',
    'tar': 'untar',
    'tar.bz2': 'untar',
    'tar.gz': 'untar',
    'tar.lzma': 'untar',
    'tar.xz': 'untar',
    'tbz': 'untar',
    'tgz': 'untar',
    'tlz': 'untar',
    'txt': 'xedit',
    'txz': 'untar',
    'wav': 'audacity',
    'wpd': 'soffice',
    'xhtml': BROWSER,
    'xls': 'soffice',
    'xlsx': 'soffice',
    'xz': 'unxz',
    'zip': 'un7z',
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

        for file in options.get_files():
            if os.path.isdir(file):
                self._spawn('xdesktop', file)
            elif file.split(':', 1)[0] in URL_PREFIXS:
                self._spawn(BROWSER, file)
            elif not os.path.isfile(file):
                print(file + ': cannot find file.')
            else:
                command = MAPPINGS.get(
                    '.'.join(file.rsplit('.', 2)[-2:]).lower()
                )
                if command:
                    self._spawn(command, file)
                else:
                    command = MAPPINGS.get(file.rsplit('.', 1)[-1].lower())
                    if command:
                        self._spawn(command, file)
                    else:
                        print(file + ': unknown file extension.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
