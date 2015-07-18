#!/usr/bin/env python3
"""
Download http/https/ftp/file URLs.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal
import socket
import time
import urllib.request

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])


    def getUrls(self):
        """
        Return list of urls.
        """
        return self._args.urls


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Download http/https/ftp/file URLs.")

        parser.add_argument("urls", nargs="+", metavar="url", help="http/https/ftp/file URL.")

        self._args = parser.parse_args(args)


class Download(syslib.Dump):


    def __init__(self, options):
        self._chunkSize = 131072
        self._urls = options.getUrls()


    def _getFileStat(self, url, res):
        """
        url = URL to download
        res = http.client.HTTPResponse object

        Returns (filename, size, time) tuple.
        """
        info = res.info()
        try:
            mtime = time.mktime(time.strptime(
                    info.get("Last-Modified"), "%a, %d %b %Y %H:%M:%S %Z"))
        except TypeError:
            # For directories
            file = "index.html"
            mtime = time.time()
        else:
            file = os.path.basename(url)

        try:
            size = int(info.get("Content-Length"))
        except TypeError:
            size = -1

        if os.path.isfile(file):
            file +=  "-" + str(os.getpid())

        return (file, size, mtime)


    def _get(self, url):
        print(url)

        try:
            with urllib.request.urlopen(url) as ifile:
                file, size, mtime = self._getFileStat(url, ifile)
                tmpfile = file + ".part"

                tmpsize = 0
                try:
                    with open(tmpfile, "wb") as ofile:
                        while True:
                            chunk = ifile.read(self._chunkSize)
                            if not chunk:
                                break
                            tmpsize += len(chunk)
                            ofile.write(chunk)
                            print("\r  => {0:s} [{1:d}/{2:d}]".format(file, tmpsize, size), end="")
                except PermissionError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" file.')
                print()

                os.utime(tmpfile, (mtime, mtime))
                try:
                    os.rename(tmpfile, file)
                except OSError:
                    pass

        except urllib.error.URLError as exception:
            reason = exception.reason
            if type(reason) == socket.gaierror:
                raise SystemExit(sys.argv[0] + ": " + reason.args[1] +".")
            elif "Not Found" in reason:
                raise SystemExit(sys.argv[0] + ": 404 Not Found.")
            elif "Permission denied" in reason:
                raise SystemExit(sys.argv[0] + ": 550 Permission denied.")
            else:
                raise SystemExit(sys.argv[0] + ": " + exception.args[0])
        except ValueError as exception:
            raise SystemExit(sys.argv[0] + ": " + exception.args[0])


    def run(self):
        for url in self._urls:
            self._get(url)


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Download(options).run()
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
            files = glob.glob(arg) # Fixes Windows globbing bug
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
