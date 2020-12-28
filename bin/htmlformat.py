#!/usr/bin/env python3
"""
Re-format HTML file.
"""

import argparse
import glob
import os
import re
import shutil
import signal
import sys

import bs4

import command_mod
import subtask_mod


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
        parser = argparse.ArgumentParser(description='Re-format HTML file.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File to change.'
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
    _indent = re.compile(r'^(\s*)', re.MULTILINE)
    _xmllint = command_mod.Command('xmllint', errors='stop')

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
    def _reformat(cls, file):
        lines = []
        try:
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    lines.append(line.strip())
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" file.'
            ) from exception
        soup = bs4.BeautifulSoup(
            ''.join(lines).replace('&', '&amp;'),
            'html.parser'
        )
        html_text = cls._indent.sub(r'\1\1', soup.prettify())

        tmpfile = file + '.part'
        try:
            with open(tmpfile, 'w', newline='\n') as ofile:
                print(html_text.replace('&amp;', '&'), file=ofile)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + tmpfile + '" file.'
            ) from exception
        try:
            shutil.move(tmpfile, file)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot rename "' + tmpfile +
                '" file to "' + file + '".'
            ) from exception

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        errors = False
        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')

            if file.endswith(('htm', 'html', 'xhtml')):
                print('Re-formatting "' + file + '" HTML file...')

                task = subtask_mod.Batch(cls._xmllint.get_cmdline() + [file])
                task.run()
                if task.has_error():
                    for line in task.get_error():
                        print(line, file=sys.stderr)
                    errors = True
                else:
                    cls._reformat(file)

        return errors


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
