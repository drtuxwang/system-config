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

    def _get_package_list(self, url):
        archive = os.path.basename(url)
        if not url.startswith('http://') or archive not in (
                'Packages.xz', 'Packages.bz2', 'Packages.gz'):
            raise SystemExit(sys.argv[0] + ': Invalid "' + url + '" URL.')
        self._remove()
        task = subtask_mod.Batch(self._wget.get_cmdline() + [url])
        task.run()
        if task.is_match_error(' saved '):
            print('  [' + file_mod.FileStat(archive).get_time_local() + ']', url)
        elif not task.is_match_error('^Server file no newer'):
            print('  [File Download Error]', url)
            self._remove()
            raise SystemExit(1)
        elif task.get_exitcode():
            self._remove()
            raise SystemExit(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                             ' received from "' + task.get_file() + '".')
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

    @staticmethod
    def _remove():
        try:
            os.remove('Packages')
            os.remove('Packages.bz2')
        except OSError:
            pass

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

    def run(self):
        """
        Start program
        """
        os.umask(int('022', 8))

        options = Options()

        self._wget = command_mod.Command('wget', args=['--timestamping'], errors='stop')
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
                    shutil.move(file + '-new', file)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" file.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
