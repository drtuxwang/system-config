#!/usr/bin/env python3
"""
Extracts Javascript from a HTML file.
"""

import argparse
import glob
import os
import signal
import sys

import jsbeautifier


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
            description='Extracts Javascript from a HTML file.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='HTML file.'
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
    def _extract(file):
        lines = []
        try:
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    lines.append(line.strip().replace('SCRIPT>', 'script>'))
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read ' + file + ' HTML file.')

        for match in ' '.join(lines).split('<script>')[1:]:
            yield match.split('</script>')[0]

    @staticmethod
    def _write(file, script):
        lines = jsbeautifier.beautify(script).split('\n')
        print('Writing "{0:s}" with {1:d} lines...'.format(file, len(lines)))
        try:
            with open(file, 'w') as ofile:
                for line in lines:
                    print(line, file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot write "' + file +
                '" configuration file.')

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" HTML file.')
            number = 0
            for script in cls._extract(file):
                number += 1
                jsfile = '{0:s}-{1:02d}.js'.format(
                    file.rsplit('.', 1)[0], number)
                cls._write(jsfile, script)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
