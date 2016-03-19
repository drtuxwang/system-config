#!/usr/bin/env python3
"""
Securely connect to VNC server using SSH protocol.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_vncviewer(self):
        """
        Return vncviewer Command class object.
        """
        return self._vncviewer

    @staticmethod
    def _getport(remote_host, remote_port):
        lsof = command_mod.Command('lsof', args=['-i', 'tcp:5901-5999'], errors='stop')
        task = subtask_mod.Batch(lsof.get_cmdline())
        task.run()
        for local_port in range(5901, 6000):
            if not task.is_match_output(':' + str(local_port) + '[ -]'):
                ssh = command_mod.Command('ssh', errors='stop')
                ssh.set_args(['-f', '-L', str(local_port) + ':localhost:' + remote_port,
                              remote_host, 'sleep', '64'])
                print('Starting "ssh" port forwarding from "localhost:' + str(local_port) +
                      '" to "' + remote_host + ':' + remote_port + '"...')
                subtask_mod.Task(ssh.get_cmdline()).run()
                return str(local_port)
        raise SystemExit(sys.argv[0] + ': Cannot find unused local port in range 5901-5999.')

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Securely connect to VNC server using SSH protocol.')

        parser.add_argument('server', nargs=1, metavar='[[user]@host]:port',
                            help='VNC server location.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        try:
            remote_host, remote_port = self._args.server[0].split(':')
        except ValueError:
            raise SystemExit(
                sys.argv[0] + ': You must specific a single ":" in VNC server location.')

        try:
            if int(remote_port) < 101:
                remote_port = str(int(remote_port) + 5900)
        except ValueError:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer '
                             'for port number.')

        self._vncviewer = command_mod.Command('vncviewer', errors='stop')
        if remote_host:
            local_port = self._getport(remote_host, remote_port)
            print('Starting "vncviewer" connection via "localhost:' + local_port + '" to "' +
                  remote_host + ':' + remote_port + '"...')
        else:
            local_port = remote_port
            print('Starting "vncviewer" connection to "localhost:' + local_port + '"...')
        self._vncviewer.set_args([':' + local_port])


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
    def run():
        """
        Start program
        """
        options = Options()

        subtask_mod.Daemon(options.get_vncviewer().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
