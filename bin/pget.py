#!/usr/bin/env python3
"""
Picture downloader for Instagram website (uses curl/wget).
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_wget(self):
        """
        Return wget Command class object.
        """
        return self._wget

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Picture downloader for Instagram (uses curl/wget).')

        parser.add_argument(
            'url',
            nargs=1,
            help='Youtube or compatible video URL.'
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _get_image(url):
        curl = command_mod.Command('curl', args=[url], errors='stop')
        task = subtask_mod.Batch(curl.get_cmdline())
        task.run()

        if 'www.instagram.com/p/' in url:
            for line in task.get_output():
                if '"og:image" content="' in line:
                    return line.split('"og:image" content="')[1].split('"')[0]
            raise SystemExit(
                sys.argv[0] + ': cannot determine picture url: ' + url
            )

        raise SystemExit(sys.argv[0] + ': No video stream: ' + url)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        url = self._get_image(self._args.url[0])
        file = os.path.basename(url).split('?')[0]

        self._wget = command_mod.Command('wget', errors='stop')
        self._wget.set_args(['--output-document', file, url])


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

        subtask_mod.Exec(options.get_wget().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
