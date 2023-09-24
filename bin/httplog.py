#!/usr/bin/env python3
"""
A simple Python HTTP request logger
"""

import argparse
import http.server
import signal
import sys
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_port(self) -> int:
        """
        Return port.
        """
        return self._args.port[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="A simple Python HTTP request logger.",
        )

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


class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP requests logger class
    """

    def _send_response(self) -> None:
        """
        Send OK response
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self) -> None:  # pylint: disable=invalid-name
        """
        Log GET request
        """
        print(f"\nGET Path: {self.path}")
        print(f"GET Headers: {self.headers}", end='')
        self._send_response()

    def do_POST(self) -> None:  # pylint: disable=invalid-name
        """
        Log POST request
        """
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length)
        print(f"\nPOST Path: {self.path}")
        print(f"POST Data: {data.decode(errors='replace')}")
        print(f"POST Headers: {self.headers}", end='')
        self._send_response()


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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()
        port = options.get_port()

        httpd = http.server.HTTPServer(('', port), HTTPRequestHandler)
        httpd.serve_forever()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
