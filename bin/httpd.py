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
from pathlib import Path
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_directory(self) -> str:
        """
        Return directory.
        """
        return self._args.directory[0]

    def get_port(self) -> int:
        """
        Return port.
        """
        return self._args.port[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Start a simple Python HTTP server.",
        )

        parser.add_argument('directory', nargs=1, help="Directory to serve.")
        parser.add_argument(
            'port',
            nargs=1,
            type=int,
            help="Port number to bind to.",
        )

        self._args = parser.parse_args(args)

        if self._args.port[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a positive integer for '
                'port number.',
            )

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        directory = self._args.directory[0]
        if not Path(directory).is_dir():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "{directory}" directory.',
            )

        try:
            self._port = int(args[2])
        except ValueError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Invalid port number "{args[2]}".',
            ) from exception


class MyTCPServer(socketserver.TCPServer):
    """
    Enable immediate port reuse.
    """

    def server_bind(self) -> None:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        try:
            os.chdir(options.get_directory())
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot change to '
                f'"{options.get_directory()}" directory.',
            ) from exception

        port = options.get_port()
        http.server.SimpleHTTPRequestHandler.extensions_map['.log'] = (
            'text/plain')

        try:
            httpd = MyTCPServer(
                ('', port),
                http.server.SimpleHTTPRequestHandler
            )
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot bind to address "localhost:{port}".',
            ) from exception

        print(f'Serving "{os.getcwd()}" at "http://localhost:{port}"...')
        httpd.serve_forever()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
