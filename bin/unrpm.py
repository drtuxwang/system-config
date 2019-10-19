#!/usr/bin/env python3
"""
Unpack a compressed archive in RPM format.
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

    def get_archives(self):
        """
        Return list of archive files.
        """
        return self._args.archives

    def get_cpio(self):
        """
        Return cpio Command class object.
        """
        return self._cpio

    def get_rpm2cpio(self):
        """
        Return rpm2cpio Command class object.
        """
        return self._rpm2cpio

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a compressed archive in RPM format.')

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show contents of archive.'
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.rpm',
            help='Archive file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._rpm2cpio = command_mod.Command('rpm2cpio', errors='stop')
        self._cpio = command_mod.Command('cpio', errors='stop')
        if self._args.view_flag:
            self._cpio.set_args(['-idmt', '--no-absolute-filenames'])
        else:
            self._cpio.set_args(['-idmv', '--no-absolute-filenames'])


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

        os.umask(int('022', 8))
        cpio = options.get_cpio()
        rpm2cpio = options.get_rpm2cpio()

        for archive in options.get_archives():
            if not os.path.isfile(archive):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + archive +
                    '" archive file.'
                )
            print(archive + ':')
            task = subtask_mod.Task(
                rpm2cpio.get_cmdline() + [archive, '|'] + cpio.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
