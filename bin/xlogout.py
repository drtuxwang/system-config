#!/usr/bin/env python3
"""
Shutdown X-windows
"""

import argparse
import glob
import os
import signal
import sys

import task_mod

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_force_flag(self):
        """
        Return force flag.
        """
        return self._args.force_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Logout from X-windows desktop.')

        parser.add_argument('-force', dest='force_flag', action='store_true',
                            help='Force login without confirmation.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

    def run(self):
        """
        Start program
        """
        options = Options()

        self._pid = 0
        if 'SESSION_MANAGER' in os.environ:
            try:
                self._pid = int(os.path.basename(os.environ['SESSION_MANAGER']))
            except ValueError:
                pass

        if not options.get_force_flag():
            try:
                answer = input('Do you really want to logout of X-session? (y/n) [n] ')
                if answer.lower() != 'y':
                    raise SystemExit(1)
            except EOFError:
                pass
            except KeyboardInterrupt:
                sys.exit(114)

        task_mod.Tasks.factory().killpids([self._pid])


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
