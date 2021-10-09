#!/usr/bin/env python3
"""
Extract Facebook friends list from saved HTML file.
"""

import argparse
import glob
import os
import re
import signal
import sys
import time
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_file(self) -> str:
        """
        Return html file.
        """
        return self._args.file[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Extract Facebook friends list from saved HTML file.',
        )

        parser.add_argument('file', nargs=1, help='HTML file.')

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Profile:
    """
    Profile class
    """

    def __init__(self, name: str, url: str) -> None:
        self._name = name
        self._url = url

    def get_name(self) -> str:
        """
        Return name.
        """
        return self._name

    def get_url(self) -> str:
        """
        Return url.
        """
        return self._url


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

    def _read_html(self, file: str) -> None:
        isjunk = re.compile('(&amp;|[?])ref=pb$|[?&]fref=.*|&amp;.*')
        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                for line in ifile:
                    for block in line.split('href="'):
                        if '://www.facebook.com/' in block:
                            if ('hc_location=friends_tab' in
                                    block.split("'")[0]):
                                url = isjunk.sub('', block.split(
                                    "'")[0]).replace(
                                        '?hc_location=friend_browser', '')
                                uid = int(block.split('user.php?id=')[1].split(
                                    '"')[0].split('&')[0])
                                name = block.split('>')[1].split('<')[0]
                                self._profiles[uid] = Profile(name, url)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" HTML file.'
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._profiles: dict = {}
        self._read_html(options.get_file())

        file = time.strftime('facebook-%Y%m%d.csv', time.localtime())
        print(
            'Writing "' + file + '" with',
            len(self._profiles.keys()),
            "friends..."
        )
        try:
            with open(file, 'w', encoding='utf-8', newline='\n') as ofile:
                print("uid,name,profile_url", file=ofile)
                for uid, profile in sorted(self._profiles.items()):
                    if uid < 0:
                        print("???", end='', file=ofile)
                    else:
                        print(uid, end='', file=ofile)
                    if ' ' in profile.get_name():
                        print(',"{0:s}",{1:s}'.format(
                            profile.get_name(), profile.get_url()), file=ofile)
                    else:
                        print(",{0:s},{1:s}".format(
                            profile.get_name(), profile.get_url()), file=ofile)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + file + '" CSV file.'
            ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
