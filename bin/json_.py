#!/usr/bin/env python3
"""
Convert JSON/YAML to JSON file.
"""

import argparse
import glob
import json
import os
import shutil
import signal
import sys

import yaml

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Convert JSON/YAML to JSON file.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File to convert.'
        )

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

    @staticmethod
    def _write_json(file, data):
        tmpfile = file + '-tmp' + str(os.getpid())
        json_data = json.dumps(data, indent=4, sort_keys=True)

        try:
            with open(tmpfile, 'w', newline='\n') as ofile:
                print(json_data, file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + tmpfile + '" file.')
        try:
            shutil.move(tmpfile, file)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot rename "' + tmpfile +
                '" file to "' + file + '".'
            )

    @classmethod
    def _convert(cls, file):
        json_file = file.rsplit('.')[0] + '.json'
        print('Converting "{0:s}" to "{1:s}"...'.format(file, json_file))
        try:
            with open(file) as ifile:
                if file.endswith('.json'):
                    data = json.load(ifile)
                else:
                    data = yaml.load(ifile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "{0:s}" file.'.format(file))
        cls._write_json(json_file, data)

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            elif file.endswith(('.json', 'yaml', 'yml')):
                cls._convert(file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
