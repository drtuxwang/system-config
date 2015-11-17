#!/usr/bin/env python3
"""
Multi-threaded download accelerator.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import shutil
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._aria2c = syslib.Command('aria2c')
        self._aria2c.setFlags(['--file-allocation=none', '--remote-time=true'])
        self._setLibraries(self._aria2c)

        self._setProxy()

    def getThreads(self):
        """
        Return number of threads.
        """
        return self._args.threads[0]

    def getUrls(self):
        """
        Return list of urls.
        """
        return self._args.urls

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Multi-threaded download accelerator.')

        parser.add_argument('-threads', nargs=1, type=int, default=[4],
                            help='Number of threads. Default is 4.')

        parser.add_argument('urls', nargs='+', metavar='url|file.url',
                            help='URL or file containing URLs.')

        self._args = parser.parse_args(args)

        if self._args.threads[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'number of threads.')

    def getAria2c(self):
        """
        Return aria2c Command class object.
        """
        return self._aria2c

    def _setLibraries(self, command):
        libdir = os.path.join(os.path.dirname(command.getFile()), 'lib')
        if os.path.isdir(libdir):
            if syslib.info.getSystem() == 'linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        libdir + os.pathsep + os.environ['LD_LIBRARY_PATH'])
                else:
                    os.environ['LD_LIBRARY_PATH'] = libdir

    def _setProxy(self):
        setproxy = syslib.Command('setproxy', check=False)
        if setproxy:
            setproxy.run(mode='batch')
            if setproxy.hasOutput():
                proxy = setproxy.getOutput()[0].strip()
                if proxy:
                    self._aria2c.extendFlags(['--all-proxy=http://' + proxy])


class Geturl(syslib.Dump):

    def __init__(self, options):
        self._options = options

    def run(self):
        os.umask(int('022', 8))
        aria2c = self._options.getAria2c()

        for url in self._options.getUrls():
            filesLocal = []
            if url.endswith('.url') and os.path.isfile(url):
                directory = url[:-4]
                filesRemote = []
                aria2c.setArgs(['--max-concurrent-downloads=' + str(self._options.getThreads()),
                                '--dir=' + directory, '-Z'])
                try:
                    with open(url, errors='replace') as ifile:
                        for line in ifile:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if line.startswith('file://'):
                                    if line not in filesLocal:
                                        filesLocal.append(line.replace('file://', '', 1))
                                elif line not in filesRemote:
                                    filesRemote.append(line)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + url + '" URL file.')
            elif os.path.isdir(url):
                raise SystemExit(sys.argv[0] + ': Cannot process "' + url + '" directory.')
            else:
                aria2c.setArgs(['--split=' + str(self._options.getThreads())])
                filesRemote = [url]
            if filesLocal:
                if not os.path.isdir(directory):
                    try:
                        os.mkdir(directory)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' + directory + '" directory.')
                for file in filesLocal:
                    print('file://' + file)
                    try:
                        shutil.copy2(file, os.path.join(directory, os.path.basename(file)))
                    except IOError:
                        raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            if filesRemote:
                for file in filesRemote:
                    aria2c.appendArg(file.replace('https://', 'http://'))
                aria2c.run()
                if aria2c.getExitcode():
                    raise SystemExit(sys.argv[0] + ': Error code ' + str(aria2c.getExitcode()) +
                                     ' received from "' + aria2c.getFile() + '".')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Geturl(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
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
