#!/usr/bin/env python3
"""
Run command on a list of nodes in parallel.
"""

import argparse
import glob
import logging
import logging.handlers
import os
import queue
import signal
import subprocess
import sys
import time
import threading

import paramiko

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_threads(self):
        """
        Return number of threads.
        """
        return self._args.threads[0]

    def get_timeout(self):
        """
        Return timeout in seconds.
        """
        return self._args.timeout[0]

    def get_nodes(self):
        """
        Return nodes ist.
        """
        return self._nodes

    def get_cmdline(self):
        """
        Return the command line as a list.
        """
        return self._cmdline

    @staticmethod
    def _parse_input():
        nodes = []
        for line in sys.stdin:
            nodes.extend(line.split())
        return nodes

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Run command on a list of nodes in parallel '
            '(supply node list as stdin).\n'
        )

        parser.add_argument(
            '-threads',
            nargs=1,
            type=int,
            dest='threads',
            default=[16],
            metavar='N',
            help='Select number of threads. Default is 16.'
        )
        parser.add_argument(
            '-timeout',
            nargs=1,
            type=int,
            dest='timeout',
            default=[60],
            metavar='seconds',
            help='Select timeout in seconds. Default is 60.'
        )
        parser.add_argument(
            'command',
            nargs=1,
            help='Command to run on all systems.'
        )
        parser.add_argument(
            'args',
            nargs='*',
            metavar='arg',
            help='Command arguments.'
        )

        my_args = []
        while args:
            my_args.append(args[0])
            if not args[0].startswith('-'):
                break
            elif args[0] == '-threads' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            elif args[0] == '-timeout' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(my_args)
        return args

    def parse(self, args):
        """
        Parse arguments
        """
        self._cmdline = self._parse_args(args[1:])
        self._nodes = self._parse_input()


class SecureShell(object):
    """
    SecureShell class
    """

    def __init__(self):
        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._host = None

    def connect(self, host):
        """
        Connect to host
        """
        username, self._host = host.split('@', 1)

        try:
            with open(os.devnull, 'w') as sys.stderr:
                self._client.connect(
                    self._host,
                    username=username,
                    look_for_keys=False,
                    timeout=4
                )
        except Exception as exception:
            self.close()
            raise SecureShellError(exception)

    def execute(self, command, timeout):
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
            with open(self._host + '.txt', 'a', newline='\n') as ofile:
                print(
                    time.strftime('%Y-%m-%d-%H:%M:%S: connected'), file=ofile)
                for line in stdout:
                    print(line.rstrip('\r\n'), file=ofile)
        except Exception as exception:
            self.close()
            raise SecureShellError(exception)

    def close(self):
        """
        Disconnect from host
        """
        self._client.close()


class WorkQueue(object):
    """
    WorkQueue class
    """

    def __init__(self, threads, command, timeout):
        """
        threads = Number of threads
        command = Command list
        timeout = Execution no data time out
        """
        self._time0 = time.time()
        self._nitems = 0
        self._queue = queue.Queue(maxsize=0)

        self._workers = []
        for _ in range(threads):
            worker = threading.Thread(
                target=self._do_work,
                args=(command, timeout),
                daemon=True
            )
            worker.start()
            self._workers.append(worker)

    def _do_work(self, command, timeout):
        while True:
            host = self._queue.get()
            if host is None:
                break
            elif '@' not in host:
                host = 'root@' + host
            ssh = SecureShell()

            try:
                ssh.connect(host)
                ssh.execute(subprocess.list2cmdline(command), timeout)
                ssh.close()
            except SecureShellError as exception:
                message = str(exception)
                logging.warning(host + ': ' + message)
            else:
                message = 'ok'
            print('[{0:d}/{1:d},{2:d}] {3:s}: {4:s}'.format(
                self._nitems - self._queue.qsize() + 1, self._nitems,
                int(time.time() - self._time0), host, message))
            self._queue.task_done()

    def add_items(self, hosts):
        """
        Add items to queue
        """
        self._nitems += len(hosts)
        for host in hosts:
            self._queue.put(host)

    def join(self):
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


class Main(object):
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
    def _config_logging():
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
    def _config_directory():
        directory = 'cluster.results'
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except OSError:
                message = 'Cannot create "' + directory + '" directory.'
                logging.error(message)
                raise SystemExit(sys.argv[0] + ': ' + message)
        try:
            os.chdir(directory)
        except OSError:
            message = 'Cannot change to "' + directory + '" directory.'
            logging.error(message)
            raise SystemExit(sys.argv[0] + ': ' + message)

    def run(self):
        """
        Start program
        """
        self._options = Options()
        nodes = self._options.get_nodes()
        threads = min(len(nodes), self._options.get_threads())

        self._config_logging()
        self._config_directory()
        logging.info(50 * '-')
        logging.info('INIT %d threads: run on %d nodes', threads, len(nodes))

        work_queue = WorkQueue(
            threads,
            self._options.get_cmdline(),
            self._options.get_timeout()
        )
        work_queue.add_items(nodes)
        work_queue.join()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
