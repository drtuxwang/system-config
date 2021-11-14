#!/usr/bin/env python3
"""
Picture downloader for Instagram website.
"""

import argparse
import glob
import os
import signal
import sys
import time
from typing import List, Set

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_urls(self) -> Set[str]:
        """
        Return image urls.
        """
        return self._urls

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Picture downloader for websites.",
        )

        parser.add_argument(
            'url',
            nargs=1,
            help="Website URL.",
        )

        self._args = parser.parse_args(args)

    @staticmethod
    def _parse_instagram(task: subtask_mod.Task) -> Set[str]:

        while True:
            task.run()
            text = ' '.join(task.get_output())
            if "Login • Instagram" not in text:
                break
            url = task.get_cmdline()[3]
            print(f"{url}: Login issue retry in 60s", file=sys.stderr)
            time.sleep(60)

        urls = text.split('display_url":"')[1:]
        return {url.split('"')[0].replace('\\u0026', '&') for url in urls}

    @classmethod
    def _get_images(cls, url: str) -> Set[str]:
        wget = command_mod.Command(
            'wget',
            args=['-O', '-', url],
            errors='stop'
        )
        task = subtask_mod.Batch(wget.get_cmdline())

        if 'www.instagram.com/p/' in url:
            urls = cls._parse_instagram(task)
        else:
            raise SystemExit(f"{sys.argv[0]}: Cannot handle website: {url}")

        if not urls:
            raise SystemExit(f"{sys.argv[0]}: Cannot parse images: {url}")
        return urls

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._urls = self._get_images(self._args.url[0])


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        wget = command_mod.Command('wget', errors='stop')
        for url in options.get_urls():
            file = os.path.basename(url).split('?')[0]
            wget.set_args(['--output-document', file, url])
            subtask_mod.Task(wget.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
