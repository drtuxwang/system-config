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

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_file(self):
        """
        Return html file.
        """
        return self._args.file[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Extract Facebook friends list from saved HTML file.')

        parser.add_argument('file', nargs=1, help='HTML file.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Profile(object):
    """
    Profile class
    """

    def __init__(self, name, url):
        self._name = name
        self._url = url

    def get_name(self):
        """
        Return name.
        """
        return self._name

    def get_url(self):
        """
        Return url.
        """
        return self._url


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

    def _read_html(self, file):
        isjunk = re.compile('(&amp;|[?])ref=pb$|[?&]fref=.*|&amp;.*')
        try:
            with open(file, errors='replace') as ifile:
                for line in ifile:
                    for block in line.split('href="'):
                        if '://www.facebook.com/' in block:
                            if 'hc_location=friends_tab' in block.split("'")[0]:
                                url = isjunk.sub('', block.split("'")[0]).replace(
                                    '?hc_location=friend_browser', '')
                                uid = int(block.split('user.php?id=')[1].split(
                                    '"')[0].split('&')[0])
                                name = block.split('>')[1].split('<')[0]
                                self._profiles[uid] = Profile(name, url)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" HTML file.')

    def run(self):
        """
        Start program
        """
        options = Options()

        self._profiles = {}
        self._read_html(options.get_file())

        file = time.strftime('facebook-%Y%m%d.csv', time.localtime())
        print('Writing "' + file + '" with', len(self._profiles.keys()), 'friends...')
        try:
            with open(file, 'w', newline='\n') as ofile:
                print('uid,name,profile_url', file=ofile)
                for uid, profile in sorted(self._profiles.items()):
                    if uid < 0:
                        print('???', end='', file=ofile)
                    else:
                        print(uid, end='', file=ofile)
                    if ' ' in profile.get_name():
                        print(',"' + profile.get_name() + '",' + profile.get_url(), file=ofile)
                    else:
                        print(',' + profile.get_name() + ',' + profile.get_url(), file=ofile)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" CSV file.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
