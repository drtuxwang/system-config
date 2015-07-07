#!/usr/bin/env python3
"""
Start a simple Python HTTP server.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import http.server
import os
import signal
import socketserver

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])

        directory = self._args.directory[0]
        if not os.path.isdir(directory):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + directory + '" directory.')

        try:
            self._port = int(args[2])
        except ValueError:
            raise SystemExit(sys.argv[0] + ': Invalid port number "' + args[2] + '".')


    def getDirectory(self):
        """
        Return directory.
        """
        return self._args.directory[0]


    def getPort(self):
        """
        Return port.
        """
        return self._args.port[0]


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Start a simple Python HTTP server.")

        parser.add_argument("directory", nargs=1, help="Directory to serve.")
        parser.add_argument("port", nargs=1, type=int, help="Port number to bind to.")

        self._args = parser.parse_args(args)

        if self._args.port[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "port number.")


class WebServer(syslib.Dump):


    def __init__(self, options):
        try:
            os.chdir(options.getDirectory())
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot change to "' +
                             options.getDirectory() + '" directory.')

        self._port = options.getPort()
        self._mineTypes()


    def run(self):
        try:
            httpd = socketserver.TCPServer(("", self._port), http.server.SimpleHTTPRequestHandler)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot bind to address "localhost:' +
                             str(self._port) + '".')

        print('Serving "' + os.getcwd() + '" at "http://localhost:' + str(self._port) + '"...')
        httpd.serve_forever()


    def _mineTypes(self):
        http.server.SimpleHTTPRequestHandler.extensions_map[".log"] = "text/plain"


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            WebServer(options).run()
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
