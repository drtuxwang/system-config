#!/usr/bin/env python3
"""
Streaming video downloader (Youtube, m3u8 and compatible websites).
"""

import argparse
import glob
import os
import signal
import sys
import time
import urllib.request

import command_mod
import config_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._mtime = None
        self._output = ''
        self.parse(sys.argv)

    def get_mtime(self):
        """
        Return output file modification time.
        """
        return self._mtime

    def get_output(self):
        """
        Return output file.
        """
        return self._output

    def get_vget(self):
        """
        Return vget Command class object.
        """
        return self._vget

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Streaming video downloader '
            '(Youtube, m3u8 and compatible websites).'
        )
        parser.add_argument(
            '-f',
            nargs=1,
            dest='code',
            default=None,
            help='Select video format code (default "136+140/mp4" for 720p).'
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show video format codes.'
        )
        parser.add_argument(
            '-O',
            nargs=1,
            dest='output',
            default=None,
            help='Output file name.'
        )
        parser.add_argument(
            'url',
            nargs=1,
            help='Youtube or compatible video URL.'
        )

        self._args = parser.parse_args(args)

    def _detect_code(self, url):
        task = subtask_mod.Batch(
            self._vget.get_cmdline() + ['--list-formats', url]
        )
        task.run(pattern=r'^[^ ]+ +mp4 +\d+x\d+ ')

        codes = {}
        for line in task.get_output():
            if 'mp4' in line and 'video only' in line:
                code, _, size = line.split()[:3]
                codes[int(size.split('x')[1])] = code
        for height in sorted(codes, reverse=True):
            if height <= 720:
                return codes[height] + '+bestaudio[ext=m4a]/mp4'
        for height in sorted(codes):
            return codes[height] + '+bestaudio[ext=m4a]/mp4'

        raise SystemExit(sys.argv[0] + ': No video stream: ' + url)

    def _detect_mtime(self, url):
        task = subtask_mod.Batch(self._vget.get_cmdline() + ['--get-url', url])
        task.run(pattern=r'^http')
        if task.has_output():
            try:
                req = urllib.request.Request(task.get_output()[0], headers={
                    'User-Agent': config_mod.Config().get('user_agent'),
                })
            except (urllib.error.HTTPError, urllib.error.URLError):
                pass
            else:
                conn = urllib.request.urlopen(req)
                info = conn.info()
                try:
                    return time.mktime(time.strptime(
                        info.get('Last-Modified'),
                        '%a, %d %b %Y %H:%M:%S %Z',
                    ))
                except TypeError:
                    pass

        return None

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        url = self._args.url[0]
        if '&index=' in url:  # Fix download one video for series
            url = url.split('&')[0]
        self._vget = command_mod.CommandFile(sys.executable)
        self._vget.set_args(['-m', 'youtube_dl', '--playlist-end', '1'])

        if self._args.view_flag:
            self._vget.extend_args(['--list-formats', url])
            return

        if self._args.code:
            code = self._args.code[0]
        elif url.endswith('.m3u8'):  # Multi part streaming
            code = '0'
        else:
            code = self._detect_code(url)
        self._vget.extend_args(['--format', code])

        self._mtime = self._detect_mtime(url)

        if self._args.output:
            self._output = self._args.output[0]
            if os.path.isfile(self._output):
                raise SystemExit("Output file already exists: " + self._output)
            self._vget.extend_args(['--output', self._output])

        self._vget.append_arg(url)


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
        mtime = options.get_mtime()
        output = options.get_output()
        vget = options.get_vget()

        task = subtask_mod.Task(vget.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(task.get_exitcode())

        if mtime and output:
            os.utime(output, (mtime, mtime))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
