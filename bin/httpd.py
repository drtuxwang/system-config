#!/usr/bin/env python3
"""
Start a simple Python HTTP server.
"""

import argparse
import glob
import http.server
import os
import signal
import socket
import socketserver
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

        directory = self._args.directory[0]
        if not os.path.isdir(directory):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + directory + '" directory.')

        try:
            self._port = int(args[2])
        except ValueError:
            raise SystemExit(sys.argv[0] + ': Invalid port number "' + args[2] + '".')

    def get_directory(self):
        """
        Return directory.
        """
        return self._args.directory[0]

    def get_port(self):
        """
        Return port.
        """
        return self._args.port[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Start a simple Python HTTP server.')

        parser.add_argument('directory', nargs=1, help='Directory to serve.')
        parser.add_argument('port', nargs=1, type=int, help='Port number to bind to.')

        self._args = parser.parse_args(args)

        if self._args.port[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'port number.')


class MyTCPServer(socketserver.TCPServer):
    """
    Enable immediate port reuse.
    """

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class WebServer(object):
    """
    Web server class
    """

    def __init__(self, options):
        try:
            os.chdir(options.get_directory())
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot change to "' + options.get_directory() + '" directory.')

        self._port = options.get_port()
        self._mine_types()

    def _mine_types(self):
        http.server.SimpleHTTPRequestHandler.extensions_map['.log'] = 'text/plain'

    def run(self):
        """
        Start server
        """
        try:
            httpd = MyTCPServer(('', self._port), http.server.SimpleHTTPRequestHandler)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot bind to address "localhost:' + str(self._port) + '".')

        print('Serving "' + os.getcwd() + '" at "http://localhost:' + str(self._port) + '"...')
        httpd.serve_forever()


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
            WebServer(options).run()
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
