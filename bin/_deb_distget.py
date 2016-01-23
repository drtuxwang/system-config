#!/usr/bin/env python3
"""
Download Debian packages list files.
"""

import argparse
import glob
import os
import signal
import sys

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

    def get_distribution_files(self):
        """
        Return list of distribution files.
        """
        return self._args.distribution_files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Download Debian packages list files.')

        parser.add_argument('distribution_files', nargs='+', metavar='distribution.dist',
                            help='File containing Debian package URLs.')

        self._args = parser.parse_args(args)


class Distribution(object):
    """
    Distribution class
    """

    def __init__(self, options):
        self._wget = syslib.Command('wget', flags=['--timestamping'])
        os.umask(int('022', 8))
        for distribution_file in options.get_distribution_files():
            if distribution_file.endswith('.dist'):
                try:
                    print('Checking "' + distribution_file + '" distribution file...')
                    lines = []
                    with open(distribution_file, errors='replace') as ifile:
                        for url in ifile:
                            url = url.rstrip()
                            if url and not url.startswith('#'):
                                lines.extend(self._get_package_list(url))
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' +
                                     distribution_file + '" distribution file.')
                try:
                    file = distribution_file[:-4] + 'packages'
                    with open(file + '-new', 'w', newline='\n') as ofile:
                        for line in lines:
                            print(line, file=ofile)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '-new" file.')
                try:
                    os.rename(file + '-new', file)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" file.')

    def _get_package_list(self, url):
        archive = os.path.basename(url)
        if not url.startswith('http://') or archive not in (
                'Packages.xz', 'Packages.bz2', 'Packages.gz'):
            raise SystemExit(sys.argv[0] + ': Invalid "' + url + '" URL.')
        self._remove()
        self._wget.set_args([url])
        self._wget.run(mode='batch')
        if self._wget.is_match_error(' saved '):
            print('  [' + syslib.FileStat(archive).get_time_local() + ']', url)
        elif not self._wget.is_match_error('^Server file no newer'):
            print('  [File Download Error]', url)
            self._remove()
            raise SystemExit(1)
        elif self._wget.get_exitcode():
            self._remove()
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._wget.get_exitcode()) +
                             ' received from "' + self._wget.get_file() + '".')
        self._unpack(archive)
        site = url[:url.find('/dists/') + 1]
        lines = []
        try:
            with open('Packages', errors='replace') as ifile:
                for line in ifile:
                    if line.startswith('Filename: '):
                        lines.append(line.rstrip('\r\n').replace(
                            'Filename: ', 'Filename: ' + site, 1))
                    else:
                        lines.append(line.rstrip('\r\n'))
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "Packages" packages file.')
        self._remove()
        return lines

    def _remove(self):
        try:
            os.remove('Packages')
            os.remove('Packages.bz2')
        except OSError:
            pass

    def _unpack(self, file):
        if file.endswith('.xz'):
            syslib.Command('xz', args=['-d', file]).run()
        elif file.endswith('.bz2'):
            syslib.Command('bzip2', args=['-d', file]).run()
        elif file.endswith('.gz'):
            syslib.Command('gzip', args=['-d', file]).run()
        else:
            raise SystemExit(sys.argv[0] + ': Cannot unpack "' + file + '" package file.')


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
            Distribution(options)
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
