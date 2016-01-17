#!/usr/bin/env python3
"""
Extracts http references from a HTML file.
"""

import argparse
import glob
import os
import re
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Extracts http references from a HTML file.')

        parser.add_argument('files', nargs='+', metavar='file', help='HTML file.')

        self._args = parser.parse_args(args)


class Extract(object):
    """
    Extract class
    """

    def __init__(self, options):
        urls = []
        self._is_iframe = re.compile('<iframe.*src=', re.IGNORECASE)
        self._is_ignore = re.compile('mailto:|#', re.IGNORECASE)
        self._is_url = re.compile(r'href=.*[\'">]|onclick=.*\(', re.IGNORECASE)

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" HTML file.')
            urls.extend(self._extract(file))
        for url in sorted(set(urls)):
            print(url)

    def _extract(self, file):
        try:
            with open(file, errors='replace') as ifile:
                urls = []
                for line in ifile:
                    line = line.strip()
                    for token in self._is_iframe.sub('href=', line).split():
                        if self._is_url.match(token) and not self._is_ignore.search(token):
                            url = token[5:].split('>')[0]
                            for quote in ('"', "'"):
                                if quote in url:
                                    url = url.split(quote)[1]
                            urls.append(url)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read ' + file + ' HTML file.')
        return urls


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Extract(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
