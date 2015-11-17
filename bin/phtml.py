#!/usr/bin/env python3
"""
Generate XHTML files to view pictures.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getDirectory(self):
        """
        Return list of directory.
        """
        return self._args.directory[0]

    def getHeight(self):
        """
        Return hieght in pixels.
        """
        return self._args.height

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Generate XHTML files to view pictures.')

        parser.add_argument('-height', type=int,
                            default=600, help='Select picture height in pixels (default 600).')

        parser.add_argument('directory', nargs=1, help='Directory containing picture files.')

        self._args = parser.parse_args(args)

        if self._args.height < 1:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for picture height.')
        if not os.path.isdir(self._args.directory[0]):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.directory[0] + '" directory.')


class Gallery(syslib.Dump):

    def __init__(self, directory, height):
        self._directory = directory
        self._height = height
        try:
            self._files = [
                x for x in sorted(os.listdir(directory)) if x.split('.')[-1].lower() in (
                    'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pcx', 'svg', 'tif', 'tiff')]
        except PermissionError:
            raise SystemExit(sys.argv[0] + ': Cannot open "' + directory + '" directory.')
        self._nfiles = len(self._files)

    def _generate(self, number, file, next):
        yield ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
               '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')
        yield '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">'
        yield ''
        yield '<head>'
        yield '<title>' + self._directory + '/' + file + '</title>'
        yield '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'
        yield '</head>'
        yield '<body bgcolor="#fffff1" text="#000000" link="#0000ff vlink="#900090">'
        yield ''
        yield '<table border="0" align="center">'
        yield '<tr>'
        yield '  <td valign="top">'
        yield '  (' + str(number+1) + '/' + str(self._nfiles) + ')'
        yield '  </td>'
        yield '  <td>'
        yield '    <a href="' + next.rsplit('.', 1)[0] + '.xhtml">'
        yield '    <img src="' + file + '" height="' + str(self._height) + '"/></a>'
        yield '  </td>'
        yield '  <td>'
        yield '  </td>'
        yield '</tr>'
        yield '</table>'
        yield ''
        yield '</body></html>'

    def create(self):
        if self._files:
            directoryTime = 0
            for i in range(self._nfiles):
                file = self._files[i]

                next = self._files[(i+1) % self._nfiles]

                xhtmlFile = os.path.join(self._directory, file.rsplit('.', 1)[0]) + '.xhtml'
                try:
                    with open(xhtmlFile, 'w', newline='\n') as ofile:
                        for line in self._generate(i, file, next):
                            print(line, file=ofile)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + xhtmlFile + '" file.')

                fileTime = syslib.FileStat(os.path.join(self._directory, file)).getTime()
                os.utime(xhtmlFile, (fileTime, fileTime))
                directoryTime = max(directoryTime, fileTime)

            os.utime(self._directory, (directoryTime, directoryTime))
            return directoryTime

        return None


class Xhtml(syslib.Dump):

    def __init__(self, options):
        self._height = options.getHeight()
        self._directory = options.getDirectory()

    def _find(self, directory=''):
        if directory:
            directories = [directory]
        else:
            directories = []

        for file in glob.glob(os.path.join(directory, '*')):
            if os.path.isdir(file):
                directories.extend(self._find(file))
        return directories

    def _generate(self, fileStats):
        yield ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
               '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')
        yield '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">'
        yield ''
        yield '<head>'
        yield ('<title>Photo Galleries</title>')
        yield '<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'
        yield '</head>'
        yield '<body bgcolor="#fffff1" text="#000000" link="#0000ff" vlink="#900090">'
        yield ''
        for fileStat in fileStats:
            directory = fileStat.getFile()
            xhtmlFile = sorted(glob.glob(os.path.join(directory, '*.xhtml')))[0]
            yield '<a href="' + xhtmlFile + '" target="_blank">'
            yield directory + '</a>'
            yield '<br/>'
            yield ''
        yield '</body></html>'

    def create(self):
        try:
            os.chdir(self._directory)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot change to "' + self._directory() + '" directory.')

        fileStats = []
        for directory in self._find():
            gallery = Gallery(directory, self._height)
            if gallery.create():
                fileStats.append(syslib.FileStat(directory))
        fileStats = sorted(fileStats, key=lambda s: s.getTime(), reverse=True)

        try:
            with open('index.xhtml', 'w', newline='\n') as ofile:
                for line in self._generate(fileStats):
                    print(line, file=ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "index.xhtml" file.')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Xhtml(options).create()
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
