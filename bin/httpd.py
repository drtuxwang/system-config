#!/usr/bin/env python3
"""
Sandbox a simple Python HTTP server.
"""

import argparse
import http.server
import os
import signal
import socket
import socketserver
import sys
from pathlib import Path
from typing import List

import network_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_run_flag(self) -> bool:
        """
        Return run flag.
        """
        return self._args.run_flag

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
            description="Sandbox a simple Python HTTP server.",
        )

        parser.add_argument(
            '-run',
            dest='run_flag',
            action='store_true',
            help="Run HTTPD with out creating sandbox.",
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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def sandbox(options: Options) -> None:
        """
        Create sandbox
        """
        command = network_mod.SandboxFile(sys.executable, args=[
            '-B',
            __file__,
            '-run',
            options.get_directory(),
            options.get_port(),
        ])
        configs = [
            'net',
            f'{Path(__file__).parent}:ro',
            f"{os.environ['PWD']}:ro",
        ]
        command.sandbox(configs, errors='stop')
        task = subtask_mod.Task(command.get_cmdline())
        while task.get_exitcode() not in (114, 130):
            task.run()
            print(task.get_exitcode())

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        if not options.get_run_flag():
            cls.sandbox(options)

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
