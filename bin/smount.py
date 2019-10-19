#!/usr/bin/env python3
"""
Securely mount a file system using SSH protocol.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_sshfs(self):
        """
        Return sshfs Command class object.
        """
        return self._sshfs

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Securely mount a file system using SSH protocol.')

        parser.add_argument(
            'remote',
            nargs=1,
            metavar='user@host:/remotepath',
            help='Remote directory.'
        )
        parser.add_argument(
            'local',
            nargs=1,
            metavar='user@host:/localpath',
            help='Local directory.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        if len(args) == 1:
            mount = command_mod.Command('mount', errors='stop')
            task = subtask_mod.Batch(mount.get_cmdline())
            task.run(pattern='type fuse.sshfs ')
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )
            for line in task.get_output():
                print(line)
            raise SystemExit(0)

        self._parse_args(args[1:])

        self._sshfs = command_mod.Command('sshfs', errors='stop')
        self._sshfs.set_args([
            '-o',
            'allow_root,nonempty',
        ] + self._args.remote + self._args.local)


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

        subtask_mod.Exec(options.get_sshfs().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
