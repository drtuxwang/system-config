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

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

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
        parser = argparse.ArgumentParser(
            description='Start a simple Python HTTP server.')

        parser.add_argument('directory', nargs=1, help='Directory to serve.')
        parser.add_argument(
            'port',
            nargs=1,
            type=int,
            help='Port number to bind to.'
        )

        self._args = parser.parse_args(args)

        if self._args.port[0] < 1:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'port number.'
            )

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        directory = self._args.directory[0]
        if not os.path.isdir(directory):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + directory + '" directory.')

        try:
            self._port = int(args[2])
        except ValueError:
            raise SystemExit(
                sys.argv[0] + ': Invalid port number "' + args[2] + '".')


class MyTCPServer(socketserver.TCPServer):
    """
    Enable immediate port reuse.
    """

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class Main:
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
    def run():
        """
        Start program
        """
        options = Options()

        try:
            os.chdir(options.get_directory())
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot change to "' +
                options.get_directory() + '" directory.'
            )

        port = options.get_port()
        http.server.SimpleHTTPRequestHandler.extensions_map['.log'] = (
            'text/plain')

        try:
            httpd = MyTCPServer(
                ('', port),
                http.server.SimpleHTTPRequestHandler
            )
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot bind to address "localhost:' +
                str(port) + '".'
            )

        print(
            'Serving "' + os.getcwd() + '" at "http://localhost:' +
            str(port) + '"...'
        )
        httpd.serve_forever()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
