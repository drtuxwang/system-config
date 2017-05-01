#!/usr/bin/env python3
"""
View files using default application.
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

BROWSER = ['chrome']
MAPPINGS = {
    '7z': ['un7z', '-v'],
    'ace': ['unace', '-v'],
    'bz2': ['unbz2', '-v'],
    'csv': ['soffice'],
    'deb': ['undeb', '-v'],
    'dmg': ['undmg', '-v'],
    'doc': ['soffice'],
    'docx': ['soffice'],
    'gif': ['gqview'],
    'htm': BROWSER,
    'html': BROWSER,
    'iso': ['un7z', '-v'],
    'jar': ['un7z', '-v'],
    'jpeg': ['gqview'],
    'jpg': ['gqview'],
    'json': ['xedit'],
    'mp3': ['play'],
    'odf': ['soffice'],
    'odg': ['soffice'],
    'ods': ['soffice'],
    'odt': ['soffice'],
    'ogg': ['play'],
    'png': ['gqview'],
    'ppt': ['soffice'],
    'pptx': ['soffice'],
    'pdf': ['evince'],
    'rar': ['un7z', '-v'],
    'rpm': ['unrpm', '-v'],
    'run': ['un7z', '-v'],
    'tar': ['untar', '-v'],
    'tar.bz2': ['untar', '-v'],
    'tar.gz': ['untar', '-v'],
    'tar.lzma': ['untar', '-v'],
    'tar.xz': ['untar', '-v'],
    'tbz': ['untar', '-v'],
    'tgz': ['untar', '-v'],
    'tlz': ['untar', '-v'],
    'txt': ['xedit'],
    'txz': ['untar', '-v'],
    'wav': ['play'],
    'wpd': ['soffice'],
    'xhtml': BROWSER,
    'xls': ['soffice'],
    'xlsx': ['soffice'],
    'zip': ['un7z', '-v'],
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
    def _spawn(command, file):
        print(file + ': opening with "' + command[0] + '"...')
        program = command_mod.Command(command[0], errors='stop')
        program.set_args(command[1:] + [file])
        subtask_mod.Daemon(program.get_cmdline()).run()

    def run(self):
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if os.path.isdir(file):
                command = ['xdesktop']
            elif file.split(':', 1)[0] in URL_PREFIXS:
                command = BROWSER
            elif not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': cannot find file: ' + file)
            else:
                command = MAPPINGS.get(
                    '.'.join(file.rsplit('.', 2)[-2:]).lower()
                )
                if not command:
                    command = MAPPINGS.get(file.rsplit('.', 1)[-1].lower())
                    if not command:
                        view = command_mod.Command('view', errors='stop')
                        view.set_args([file])
                        subtask_mod.Task(view.get_cmdline()).run()
                        continue
            self._spawn(command, file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
