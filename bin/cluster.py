#!/usr/bin/env python3
"""
Run command on a list of nodes in parallel.
"""

import argparse
import logging
import logging.handlers
import os
import queue
import signal
import subprocess
import sys
import time
import threading
from pathlib import Path
from typing import List

import paramiko  # type: ignore


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_threads(self) -> int:
        """
        Return number of threads.
        """
        return self._args.threads[0]

    def get_timeout(self) -> int:
        """
        Return timeout in seconds.
        """
        return self._args.timeout[0]

    def get_nodes(self) -> List[str]:
        """
        Return nodes list.
        """
        return self._nodes

    def get_cmdline(self) -> List[str]:
        """
        Return the command line as a list.
        """
        return self._cmdline

    @staticmethod
    def _parse_input() -> List[str]:
        nodes = []
        for line in sys.stdin:
            nodes.extend(line.split())
        return nodes

    def _parse_args(self, args: List[str]) -> List[str]:
        parser = argparse.ArgumentParser(
            description="Run command on a list of nodes in parallel "
            "(supply node list as stdin).\n",
        )

        parser.add_argument(
            '-threads',
            nargs=1,
            type=int,
            dest='threads',
            default=[16],
            metavar='N',
            help="Select number of threads. Default is 16.",
        )
        parser.add_argument(
            '-timeout',
            nargs=1,
            type=int,
            dest='timeout',
            default=[60],
            metavar='seconds',
            help="Select timeout in seconds. Default is 60.",
        )
        parser.add_argument(
            'command',
            nargs=1,
            help="Command to run on all systems.",
        )
        parser.add_argument(
            'args',
            nargs='*',
            metavar='arg',
            help="Command arguments.",
        )

        my_args = []
        while args:
            my_args.append(args[0])
            if not args[0].startswith('-'):
                break
            if args[0] == '-threads' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            elif args[0] == '-timeout' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(my_args)
        return args

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._cmdline = self._parse_args(args[1:])
        self._nodes = self._parse_input()


class SecureShell:
    """
    SecureShell class
    """

    def __init__(self) -> None:
        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._host = ''

    def connect(self, host: str) -> None:
        """
        Connect to host
        """
        username, self._host = host.split('@', 1)

        try:
            with Path(os.devnull).open('w') as sys.stderr:
                self._client.connect(
                    self._host,
                    username=username,
                    look_for_keys=False,
                    timeout=4
                )
        except Exception as exception:
            self.close()
            raise SecureShellError(exception) from exception

    def execute(self, command: str, timeout: int) -> None:
        """
        Execute command on remote node

        command = Command to run
        timeout = Output timeout inseconds
        """
        try:
            _, stdout, _ = self._client.exec_command(
                command,
                get_pty=True,
                timeout=timeout
            )
            with Path(f'{self._host}.txt').open('a') as ofile:
                print(
                    time.strftime('%Y-%m-%d-%H:%M:%S: connected'),
                    file=ofile
                )
                for line in stdout:
                    print(line.rstrip('\n'), file=ofile)
        except Exception as exception:
            self.close()
            raise SecureShellError(exception) from exception

    def close(self) -> None:
        """
        Disconnect from host
        """
        self._client.close()


class WorkQueue:
    """
    WorkQueue class
    """

    def __init__(self, threads: int, command: List[str], timeout: int) -> None:
        """
        threads = Number of threads
        command = Command list
        timeout = Execution no data time out
        """
        self._time0 = time.time()
        self._nitems = 0
        self._queue: queue.Queue = queue.Queue(maxsize=0)

        self._workers = []
        for _ in range(threads):
            worker = threading.Thread(
                target=self._do_work,
                args=(command, timeout),
                daemon=True
            )
            worker.start()
            self._workers.append(worker)

    def _do_work(self, command: List[str], timeout: int) -> None:
        while True:
            host = self._queue.get()
            if host is None:
                break
            if '@' not in host:
                host = f'root@{host}'
            ssh = SecureShell()

            try:
                ssh.connect(host)
                ssh.execute(subprocess.list2cmdline(command), timeout)
                ssh.close()
            except SecureShellError as exception:
                message = str(exception)
                logging.warning('\x1b[33m%s: %s\x1b[0m', host, message)
            else:
                message = 'ok'
            print(
                f"[{self._nitems - self._queue.qsize() + 1}/"
                f"{self._nitems:d},"
                f"{int(time.time() - self._time0):d}] "
                f"{host}: "
                f"{message}",
            )
            self._queue.task_done()

    def add_items(self, hosts: List[str]) -> None:
        """
        Add items to queue
        """
        self._nitems += len(hosts)
        for host in hosts:
            self._queue.put(host)

    def join(self) -> None:
        """
        Close down queue
        """
        for worker in self._workers:
            self._queue.put(None)
        for worker in self._workers:
            worker.join()


class SecureShellError(Exception):
    """
    Secure shell class error.
    """


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
    def _config_logging() -> None:
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d-%H:%M:%S'
        )
        handler = logging.handlers.RotatingFileHandler(
            'cluster.log', maxBytes=5242880, backupCount=3)
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    @staticmethod
    def _config_directory() -> None:
        path = Path('cluster.results')
        if not path.is_dir():
            try:
                path.mkdir()
            except OSError as exception:
                message = f'Cannot create "{path}" directory.'
                logging.error('\x1b[31m%s\x1b[0m', message)
                raise SystemExit(f"{sys.argv[0]}: {message}") from exception
        try:
            os.chdir(path)
        except OSError as exception:
            message = f'Cannot change to "{path}" directory.'
            logging.error('\x1b[31m%s\x1b[0m', message)
            raise SystemExit(f"{sys.argv[0]}: {message}") from exception

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()
        nodes = self._options.get_nodes()
        threads = min(len(nodes), self._options.get_threads())

        self._config_logging()
        self._config_directory()
        logging.info(50 * '-')
        logging.info("INIT %d threads: run on %d nodes", threads, len(nodes))

        work_queue = WorkQueue(
            threads,
            self._options.get_cmdline(),
            self._options.get_timeout()
        )
        work_queue.add_items(nodes)
        work_queue.join()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
