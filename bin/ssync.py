#!/usr/bin/env python3
"""
Securely synchronize file system using SSH protocol.
"""

import argparse
import getpass
import glob
import os
import signal
import sys
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_rsync(self) -> command_mod.Command:
        """
        Return rsync Command class object.
        """
        return self._rsync

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Securely synchronize file system using '
            'SSH protocol.',
        )

        parser.add_argument(
            '-root',
            action='store_true',
            help='Select Sudo to run remote rsync.'
        )
        parser.add_argument(
            '-user',
            nargs=1,
            help='Select Sudo user to run remote rsync.'
        )
        parser.add_argument(
            'source',
            nargs=1,
            metavar='[[user1@]host1:]source',
            help='Source location.'
        )
        parser.add_argument(
            'target',
            nargs=1,
            metavar='[[user1@]host1:]target',
            help='Target location.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        ssh = command_mod.Command('ssh', errors='stop')
        self._rsync = command_mod.Command('rsync', errors='stop')

        sudo_user = None
        if self._args.user:
            sudo_user = self._args.user[0]
        elif self._args.root:
            sudo_user = 'root'

        # -axHAXDv --append-verify --progress --delete-after
        args = ['--archive']  # -rlptgoD
        if sudo_user:
            if getpass.getuser() != 'root':
                # No ownership for non-root to root
                args = [
                    '--recursive',
                    '--links',
                    '--perms',
                    '--times',
                    '--devices',
                    '--specials',
                ]
            args.append(
                '--rsync-path=SUDO_ASKPASS=/bin/ssh-askpass sudo -k -A -u ' +
                sudo_user + ' -p "[sudo] password for `whoami`@'
                '`uname -n | tr \'[A-Z]\' \'[a-z]\' | cut -f1 -d.`:" rsync',
            )
            args.append('--rsh=' + ssh.get_file() + ' -X')
        else:
            args.append('--rsh=' + ssh.get_file())
        args.extend([
            '--one-file-system',
            '--hard-links',
            '--acls',
            '--xattrs',
            '--append-verify',
            '--delete-after',
            '--info=progress2',
            '--verbose',
            self._args.source[0],
            self._args.target[0],
        ])
        self._rsync.set_args(args)


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
            sys.exit(exception)

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
                files = glob.glob(arg)  # Fixes Windows globbing bug
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

        subtask_mod.Task(options.get_rsync().get_cmdline()).run(pattern='^$')

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
