#!/usr/bin/env python3
"""
Extracts http references from a HTML file.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Extracts http references from a HTML file.")

        parser.add_argument("files", nargs="+", metavar="file", help="HTML file.")

        self._args = parser.parse_args(args)


class Extract(syslib.Dump):

    def __init__(self, options):
        urls = []
        self._isiFrame = re.compile("<iframe.*src=", re.IGNORECASE)
        self._isIgnore = re.compile("mailto:|#", re.IGNORECASE)
        self._isUrl = re.compile("href=.*[\"'>]|onclick=.*\(", re.IGNORECASE)

        for file in options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" HTML file.')
            urls.extend(self._extract(file))
        for url in sorted(set(urls)):
            print(url)

    def _extract(self, file):
        try:
            with open(file, errors="replace") as ifile:
                urls = []
                for line in ifile:
                    line = line.strip()
                    for token in self._isiFrame.sub("href=", line).split():
                        if self._isUrl.match(token) and not self._isIgnore.search(token):
                            url = token[5:].split(">")[0]
                            for quote in ('"', "'"):
                                if quote in url:
                                    url = url.split(quote)[1]
                            urls.append(url)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read " + file + " HTML file.')
        return urls


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Extract(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
