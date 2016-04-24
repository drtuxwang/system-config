#!/usr/bin/env python3
"""
Download Debian packages list files.
"""

import argparse
import functools
import glob
import os
import shutil
import signal
import sys
import time
import urllib.request

import command_mod
import file_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

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
    def _get_urls(distribution_file):
        urls = []
        try:
            with open(distribution_file, errors='replace') as ifile:
                for url in ifile:
                    url = url.rstrip()
                    if url and not url.startswith('#'):
                        if not url.startswith('http://') or os.path.basename(url) not in (
                                'Packages.xz', 'Packages.bz2', 'Packages.gz'):
                            raise SystemExit(sys.argv[0] + ': Invalid "' + url + '" URL.')
                        urls.append(url)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + distribution_file + '" distribution file.')
        return urls

    @classmethod
    def _get_packages_list(cls, wget, url):
        archive = os.path.basename(url)
        cls._remove()
        task = subtask_mod.Batch(wget.get_cmdline() + [url])
        task.run()
        if task.is_match_error(' saved '):
            print('  [' + file_mod.FileStat(archive).get_time_local() + ']', url)
        elif not task.is_match_error('^Server file no newer'):
            print('  [File Download Error]', url)
            cls._remove()
            raise SystemExit(1)
        elif task.get_exitcode():
            cls._remove()
            raise SystemExit(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                             ' received from "' + task.get_file() + '".')
        cls._unpack(archive)
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
        cls._remove()
        return lines

    @staticmethod
    def _remove():
        try:
            os.remove('Packages')
            os.remove('Packages.bz2')
        except OSError:
            pass

    @staticmethod
    def _has_changed(distribution_file, urls):
        file = distribution_file[:-4] + 'packages'
        file_time = file_mod.FileStat(file).get_time()

        for url in urls:
            try:
                conn = urllib.request.urlopen(url)
            except Exception:
                raise SystemExit('Error: Cannot fetch URL: ' + url)

            info = conn.info()
            url_time = time.mktime(time.strptime(
                info.get('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z'))
            if url_time > file_time:
                return True

        return False

    @staticmethod
    @functools.lru_cache(maxsize=4)
    def _get_cmdline(name):
        command = command_mod.Command(name, args=['-d'], errors='stop')

        return command.get_cmdline()

    @classmethod
    def _unpack(cls, file):
        if file.endswith('.xz'):
            subtask_mod.Task(cls._get_cmdline('xz') + [file]).run()
        elif file.endswith('.bz2'):
            subtask_mod.Task(cls._get_cmdline('bzip2') + [file]).run()
        elif file.endswith('.gz'):
            subtask_mod.Task(cls._get_cmdline('gzip') + [file]).run()
        else:
            raise SystemExit(sys.argv[0] + ': Cannot unpack "' + file + '" package file.')

    @classmethod
    def _update_packages_list(cls, distribution_file, wget, urls):
        lines = []
        for url in urls:
            lines.extend(cls._get_packages_list(wget, url))

        try:
            file = distribution_file[:-4] + 'packages'
            with open(file + '-new', 'w', newline='\n') as ofile:
                for line in lines:
                    print(line, file=ofile)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '-new" file.')
        try:
            shutil.move(file + '-new', file)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" file.')

    @classmethod
    def run(cls):
        """
        Start program
        """
        os.umask(int('022', 8))

        options = Options()

        wget = command_mod.Command('wget', args=['--timestamping'], errors='stop')

        for distribution_file in options.get_distribution_files():
            if distribution_file.endswith('.dist'):
                print('Checking "' + distribution_file + '" distribution file...')
                urls = cls._get_urls(distribution_file)
                if cls._has_changed(distribution_file, urls):
                    cls._update_packages_list(distribution_file, wget, urls)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
