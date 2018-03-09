#!/usr/bin/env python3
"""
Convert JSON/YAML to JSON file.
"""

import argparse
import glob
import json
import os
import re
import shutil
import signal
import sys

import yaml

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_check_flag(self):
        """
        Return check flag.
        """
        return self._args.check_flag

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Convert JSON/YAML to JSON file.')

        parser.add_argument(
            '-c',
            dest='check_flag',
            action='store_true',
            help='Check JSON/YAML format only.'
        )
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
    def _split_jsons(text):
        """
        Split multiple JSONs in string and return list of JSONs.
        """
        return re.sub('}[ \\n]*{', '}}{{', text).split('}{')

    @staticmethod
    def _split_yamls(text):
        """
        Split multiple YAMLs in string and return list of YAMLs.
        """
        return re.split('\n--', text)

    @classmethod
    def _read_file(cls, file):
        try:
            with open(file) as ifile:
                if file.endswith('.json'):
                    data = [
                        json.loads(block)
                        for block in cls._split_jsons(ifile.read())
                    ]
                else:
                    data = [
                        yaml.load(block)
                        for block in cls._split_yamls(ifile.read())
                    ]
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "{0:s}" file.'.format(file))
        return data

    @staticmethod
    def _write_json(file, data):
        tmpfile = file + '-tmp' + str(os.getpid())

        try:
            with open(tmpfile, 'w', newline='\n') as ofile:
                for block in data:
                    print(
                        json.dumps(block, indent=4, sort_keys=True),
                        file=ofile
                    )
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
                if options.get_check_flag():
                    try:
                        cls._read_file(file)
                    except (
                            json.decoder.JSONDecodeError,
                            yaml.parser.ParserError
                    ) as exception:
                        print("{0:s}: {1:s}".format(file, str(exception)))
                else:
                    name, _ = os.path.splitext(file)
                    json_file = name + '.json'
                    print('Converting "{0:s}" to "{1:s}"...'.format(
                        file,
                        json_file
                    ))
                    data = cls._read_file(file)
                    cls._write_json(json_file, data)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
