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

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

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


class Extract(object):
    """
    Extract class
    """

    def __init__(self, options):
        self._profiles = {}
        self._read_html(options.get_file())

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

    def write(self):
        """
        Write file
        """
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
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Extract(options).write()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
