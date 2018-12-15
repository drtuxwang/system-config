#!/usr/bin/env python3
"""
Download http/https/ftp/file URLs.
"""

import argparse
import glob
import json
import os
import shutil
import signal
import socket
import sys
import time
import urllib.request

import config_mod
import file_mod
import task_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._config()
        self.parse(sys.argv)

    def get_urls(self):
        """
        Return list of urls.
        """
        return self._args.urls

    @staticmethod
    def _config():
        if 'REQUESTS_CA_BUNDLE' not in os.environ:
            for file in (
                    # Debian/Ubuntu
                    '/etc/ssl/certs/ca-certificates.crt',
                    # RHEL/CentOS
                    '/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt'
            ):
                if os.path.isfile(file):
                    os.environ['REQUESTS_CA_BUNDLE'] = file
                    break

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Download http/https/ftp/file URLs.')

        parser.add_argument(
            'urls',
            nargs='+',
            metavar='url',
            help='http/https/ftp/file URL.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
    def _check_file(file, size, mtime):
        """
        Check existing file and return True if already downloaded.
        """
        file_stat = file_mod.FileStat(file)
        if file_stat.get_size() == size and file_stat.get_time() >= mtime:
            return True
        return False

    @staticmethod
    def _get_file_stat(url, conn):
        """
        url  = URL to download
        conn = http.client.HTTPResponse class object

        Returns (filename, size, time) tuple.
        """
        info = conn.info()

        try:
            mtime = time.mktime(time.strptime(
                info.get('Last-Modified'), '%a, %d %b %Y %H:%M:%S %Z'))
        except TypeError:
            # For directories
            file = 'index.html'
            if os.path.isfile(file):
                file = 'index-' + str(os.getpid()) + '.html'
            mtime = time.time()
        else:
            file = os.path.basename(url)

        try:
            size = int(info.get('Content-Length'))
        except TypeError:
            size = -1

        return file, size, mtime

    @staticmethod
    def _check_resume(file, data):
        """
        Return 'download', 'resume' or 'skip'
        """
        try:
            with open(file + '.part.json') as ifile:
                json_data = json.load(ifile)
                host = json_data['fget']['lock']['host']
                pid = json_data['fget']['lock']['pid']

                if (host == socket.gethostname().split('.')[0].lower() and
                        task_mod.Tasks.factory().haspid(pid)):
                    return 'skip'
                if json_data['fget']['data'] == data:
                    return 'resume'
        except (KeyError, OSError, ValueError):
            pass

        return 'download'

    @staticmethod
    def _write_resume(file, data):
        json_data = {
            'fget': {
                'lock': {
                    'host': socket.gethostname().split('.')[0].lower(),
                    'pid': os.getpid()
                },
                'data': data
            }
        }

        try:
            with open(file+'.part.json', 'w', newline='\n') as ofile:
                print(
                    json.dumps(json_data, indent=4, sort_keys=True),
                    file=ofile
                )
        except OSError:
            pass

    def _fetch(self, url):
        try:
            conn = urllib.request.urlopen(url)
        except Exception as exception:
            raise SystemExit(str(exception))

        file, size, mtime = self._get_file_stat(url, conn)
        if self._check_file(file, size, mtime):
            print("  => {0:s} [{1:d}/{2:d}]".format(file, size, size))
            return

        data = {'size': size, 'time': int(mtime)}
        check = self._check_resume(file, data)

        if check == 'skip':
            return
        elif 'Accept-Ranges' in conn.info() and check == 'resume':
            tmpsize = os.path.getsize(file + '.part')
            req = urllib.request.Request(url, headers={
                'Range': 'bytes='+str(tmpsize)+'-',
                'User-Agent': config_mod.Config().get('user_agent'),
            })
            conn = urllib.request.urlopen(req)
            mode = 'ab'
        else:
            tmpsize = 0
            mode = 'wb'

        self._write_resume(file, data)

        try:
            with open(file+'.part', mode) as ofile:
                while True:
                    chunk = conn.read(self._chunk_size)
                    if not chunk:
                        break
                    tmpsize += len(chunk)
                    ofile.write(chunk)
                    print("\r  => {0:s} [{1:d}/{2:d}]".format(
                        file, tmpsize, size), end='')
        except PermissionError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + file + '" file.')
        print()

        os.utime(file+'.part', (mtime, mtime))
        try:
            shutil.move(file+'.part', file)
            os.remove(file+'.part'+'.json')
        except OSError:
            pass

    def _get_url(self, url):
        print(url)

        try:
            self._fetch(url)
        except urllib.error.URLError as exception:
            reason = exception.reason
            if isinstance(reason, socket.gaierror):
                raise SystemExit(sys.argv[0] + ': ' + reason.args[1] + '.')
            elif 'Not Found' in reason:
                raise SystemExit(sys.argv[0] + ': 404 Not Found.')
            elif 'Permission denied' in reason:
                raise SystemExit(sys.argv[0] + ': 550 Permission denied.')
            else:
                raise SystemExit(sys.argv[0] + ': ' + exception.args[0])
        except ValueError as exception:
            raise SystemExit(sys.argv[0] + ': ' + exception.args[0])

    def run(self):
        """
        Start program
        """
        options = Options()

        self._chunk_size = 131072
        self._urls = options.get_urls()

        for url in self._urls:
            self._get_url(url)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
