#!/usr/bin/env python3
"""
Download Debian packages list files.
"""

import argparse
import datetime
import functools
import glob
import json
import os
import shutil
import signal
import sys
import time
import urllib.request

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


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
        parser = argparse.ArgumentParser(
            description='Download Debian packages list files.')

        parser.add_argument(
            'distribution_files',
            nargs='+',
            metavar='distribution.dist',
            help='File containing Debian package URLs.'
        )

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
                        if (not url.startswith('http://') or
                                os.path.basename(url) not in (
                                    'Packages.xz', 'Packages.bz2',
                                    'Packages.gz')):
                            raise SystemExit(
                                sys.argv[0] + ': Invalid "' + url + '" URL.')
                        urls.append(url)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + distribution_file +
                '" distribution file.'
            )
        return urls

    @staticmethod
    def _remove():
        for file in glob.glob('Packages*'):
            try:
                os.remove(file)
            except OSError:
                pass

    @staticmethod
    @functools.lru_cache(maxsize=4)
    def _get_cmdline(name):
        command = command_mod.Command(name, errors='stop')

        return command.get_cmdline()

    @classmethod
    def _unpack(cls, file):
        if file.endswith('.xz'):
            subtask_mod.Task(cls._get_cmdline('unxz') + [file]).run()
        elif file.endswith('.bz2'):
            subtask_mod.Task(cls._get_cmdline('bzip2') + ['-d', file]).run()
        elif file.endswith('.gz'):
            subtask_mod.Task(cls._get_cmdline('gzip') + ['-d', file]).run()
        else:
            raise SystemExit(
                sys.argv[0] + ': Cannot unpack "' + file + '" package file.')

    @staticmethod
    def _show_times(old_utime, new_utime):
        new_utc = datetime.datetime.fromtimestamp(new_utime)
        if old_utime:
            old_utc = datetime.datetime.fromtimestamp(old_utime)
            print("*** [{0:s}] packages metadata stored is out of date".format(
                old_utc.strftime('%Y-%m-%d-%H:%M:%S'),
            ))
        print("*** [{0:s}] packages metadata new file data fetching".format(
            new_utc.strftime('%Y-%m-%d-%H:%M:%S'),
        ))

    @classmethod
    def _get_packages(cls, data, wget, url):
        try:
            conn = urllib.request.urlopen(url)
        except Exception:
            raise SystemExit("Error: Cannot fetch URL: " + url)

        url_time = time.mktime(time.strptime(
            conn.info().get('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z'))
        if url_time > data['time']:
            cls._show_times(data['time'], url_time)
            archive = os.path.basename(url)
            cls._remove()
            task = subtask_mod.Task(wget.get_cmdline() + [url])
            task.run()
            if task.get_exitcode() != 0:
                print("  [ERROR (", task.get_exitcode, ")]", url)
                cls._remove()
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )
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
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "Packages" packages file.')
            cls._remove()
            data = {'time': url_time, 'text': lines}

        return data

    @staticmethod
    def _read_data(file):
        try:
            with open(file) as ifile:
                data = json.load(ifile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" json file.'
            )

        return data

    @staticmethod
    def _write_data(file, data):
        print('*** Creating "{0:s}" packages file...'.format(file))
        try:
            with open(file + '-new', 'w', newline='\n') as ofile:
                print(json.dumps(data), file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + file + '-new" file.')
        try:
            shutil.move(file + '-new', file)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + file + '" file.')

    @classmethod
    def run(cls):
        """
        Start program
        """
        os.umask(int('022', 8))

        options = Options()

        wget = command_mod.Command(
            'wget',
            args=['--timestamping'],
            errors='stop'
        )

        for distribution_file in options.get_distribution_files():
            if distribution_file.endswith('.dist'):
                print('*** Checking "{0:s}" distribution file...'.format(
                    distribution_file
                ))

                json_file = distribution_file[:-4] + 'json'
                if os.path.isfile(json_file):
                    distribution_data = cls._read_data(json_file)
                else:
                    distribution_data = {
                        'data': {},
                        'urls': []
                    }
                old_time = max([0] + [
                    data['time']
                    for data in distribution_data['data'].values()
                ])

                urls = cls._get_urls(distribution_file)
                for url in urls:
                    distribution_data['data'][url] = cls._get_packages(
                        distribution_data['data'].get(url, {'time': 0}),
                        wget,
                        url
                    )

                new_time = max([
                    data['time']
                    for data in distribution_data['data'].values()
                ])
                if new_time > old_time or distribution_data['urls'] != urls:
                    distribution_data['urls'] = urls
                    cls._write_data(json_file, distribution_data)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
