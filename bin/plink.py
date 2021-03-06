#!/usr/bin/env python3
"""
Create links to picture/video files.
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

    def get_depth(self):
        """
        Return directory depth
        """
        return self._args.depth[0]

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Create links to picture/video files.')

        parser.add_argument(
            '-depth',
            nargs=1,
            type=int,
            default=[1],
            help='Number of directories to ad to link name.'
        )
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
        depth = options.get_depth()
        config = config_mod.Config()
        images_extensions = (
            config.get('image_extensions') + config.get('video_extensions')
        )

        for directory in options.get_directories():
            linkdir = '_'.join(directory.split(os.sep)[-depth:])
            for file in sorted(glob.glob(os.path.join(directory, '*'))):
                if os.path.splitext(file)[1].lower() in images_extensions:
                    link = linkdir + '_' + os.path.basename(file)
                    if link.endswith(('.mp4', '.webm')):
                        link += '.gif'
                    if not os.path.islink(link):
                        try:
                            os.symlink(file, link)
                        except OSError as exception:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot create "' +
                                link + '" link.'
                            ) from exception


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
