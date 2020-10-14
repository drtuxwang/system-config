#!/usr/bin/env python3
"""
Convert BSON/JSON/XML/YAML to YAML file.
"""

import argparse
import glob
import os
import signal
import sys

import config_mod


class Options:
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
            description='Convert BSON/JSON/XML/YAML to YAML file.')

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
        data = config_mod.Data()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            if file.endswith(('.bson', '.json', '.xml', '.yaml', '.yml')):
                try:
                    data.read(file)
                except config_mod.ReadConfigError as exception:
                    raise SystemExit(
                        "{0:s}: {1:s}".format(file, str(exception))
                    ) from exception

                if file.endswith(('yaml', 'yml')):
                    yaml_file = file
                else:
                    name, _ = os.path.splitext(file)
                    yaml_file = name + '.yaml'
                print('Converting "{0:s}" to "{1:s}"...'.format(
                    file,
                    yaml_file
                ))
                try:
                    data.write(yaml_file)
                except config_mod.WriteConfigError as exception:
                    raise SystemExit(
                        "{0:s}: {1:s}".format(file, str(exception))
                    ) from exception


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
