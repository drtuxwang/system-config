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
import xml.sax

import bs4

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
    indent = re.compile(r'^(\s*)', re.MULTILINE)

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
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" file.')
        soup = bs4.BeautifulSoup(
            ''.join(lines).replace('&nbsp;', '&amp;nbsp;'),
            'html.parser'
        )
        html_text = cls.indent.sub(r'\1\1', soup.prettify())

        tmpfile = file + '-tmp' + str(os.getpid())
        try:
            with open(tmpfile, 'w', newline='\n') as ofile:
                print(html_text.replace('&amp;nbsp;', '&nbsp;'), file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + tmpfile + '" file.')
        try:
            shutil.move(tmpfile, file)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot rename "' + tmpfile +
                '" file to "' + file + '".'
            )

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        handler = xml.sax.ContentHandler()
        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            if file.endswith(('htm', 'html', 'xhtml')):
                print('Re-formatting "' + file + '" HTML file...')
                try:
                    xml.sax.parse(open(file, errors='replace'), handler)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot parse "' + file + '" XML file.')
                except Exception:
                    raise SystemExit(
                        sys.argv[0] + ': Invalid "' + file + '" XML file.')
                else:
                    cls._reformat(file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
