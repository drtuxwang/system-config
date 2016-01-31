#!/usr/bin/env python3
"""
Run a command with limited network bandwidth.
"""

import argparse
import glob
import json
import os
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_command(self):
        """
        Return command Command class object.
        """
        return self._command

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Run a command with limited network bandwidth.')

        parser.add_argument(
            '-n', nargs=1, type=int, dest='drate', default=[0],
            help='Download rate limit in KB. Default is 512 set in ".config/netnice.json".')

        parser.add_argument('command', nargs=1, help='Command to run.')
        parser.add_argument('args', nargs='*', metavar='arg', help='Command argument.')

        my_args = []
        while len(args):
            my_args.append(args[0])
            if not args[0].startswith('-'):
                break
            elif args[0] == '-n' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(my_args)

        if self._args.drate[0] < 0:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'download rate limit.')

        if os.path.isfile(self._args.command[0]):
            command = syslib.Command(file=self._args.command[0])
        else:
            file = os.path.join(os.path.dirname(args[0]), self._args.command[0])
            if os.path.isfile(file):
                command = syslib.Command(file=file)
            else:
                command = syslib.Command(self._args.command[0])
        command.set_args(args[len(my_args):])

        return command

    def parse(self, args):
        """
        Parse arguments
        """
        self._command = self._parse_args(args[1:])

        shaper = Shaper(self._args.drate[0])
        if not shaper.get_file():
            raise SystemExit(sys.argv[0] + ': Cannot find "trickle" command.')
        self._command.set_wrapper(shaper)


class Shaper(syslib.Command):
    """
    Sharper class
    """

    def __init__(self, drate=None):
        super().__init__('trickle', check=False)

        self._drate = 512
        if 'HOME' in os.environ:
            file = os.path.join(os.environ['HOME'], '.config', 'netnice.json')
            if not self.read(file):
                self.write(file)

        if drate:
            self._drate = drate

        self.set_rate(self._drate)

    def set_rate(self, drate):
        """
        Set rate

        drate = Download rate (KB)
        """
        self._drate = drate
        self.set_args(['-d', str(self._drate), '-s'])

    def read(self, file):
        """
        Read configuration file
        """
        if os.path.isfile(file):
            try:
                with open(file) as ifile:
                    data = json.load(ifile)
                    self._drate = data['netnice']['download']
            except (KeyError, OSError, ValueError):
                pass
            else:
                return True

        return False

    def write(self, file):
        """
        Write configuration file
        """
        data = {
            'netnice': {
                'download': self._drate
            }
        }
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(data, indent=4, sort_keys=True), file=ofile)
        except OSError:
            pass


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
        except (syslib.SyslibError, SystemExit) as exception:
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

        command = options.get_command()
        command.run()
        raise SystemExit(command.get_exitcode())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
