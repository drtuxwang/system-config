#!/usr/bin/env python3
"""
Create links to JPEG files.
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

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Create links to JPEG files.')

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help='Directory containing JPEG files to link.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Source directory "' + directory +
                    '" does not exist.'
                )
            if os.path.samefile(directory, os.getcwd()):
                raise SystemExit(
                    sys.argv[0] + ': Source directory "' + directory +
                    '" cannot be current directory.'
                )


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
        images_extensions = (
            config_mod.Config().get('image_extensions') + ['.webm']
        )

        for directory in options.get_directories():
            for file in sorted(glob.glob(os.path.join(directory, '*'))):
                if os.path.splitext(file)[1].lower() in images_extensions:
                    link = os.path.basename(
                        directory + '_' + os.path.basename(file))
                    if link.endswith('.webm'):
                        link = link.rsplit('.webm', 1)[0] + '.gif'
                    if not os.path.islink(link):
                        try:
                            os.symlink(file, link)
                        except OSError:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot create "' +
                                link + '" link.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
