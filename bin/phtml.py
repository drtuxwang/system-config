#!/usr/bin/env python3
"""
Generate XHTML files to view pictures.
"""

import argparse
import glob
import os
import signal
import sys

import file_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")

IMAGE_EXTS = {'bmp', 'gif', 'jpeg', 'jpg', 'pcx', 'png', 'svg', 'tif', 'tiff'}


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_directory(self):
        """
        Return list of directory.
        """
        return self._args.directory[0]

    def get_height(self):
        """
        Return hieght in pixels.
        """
        return self._args.height

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Generate XHTML files to view pictures.')

        parser.add_argument(
            '-height',
            type=int,
            default=600,
            help='Select picture height in pixels (default 600).'
        )
        parser.add_argument(
            'directory',
            nargs=1,
            help='Directory containing picture files.'
        )

        self._args = parser.parse_args(args)

        if self._args.height < 1:
            raise SystemExit(
                sys.argv[0] +
                ': You must specific a positive integer for picture height.'
            )
        if not os.path.isdir(self._args.directory[0]):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.directory[0] +
                '" directory.'
            )

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Gallery(object):
    """
    Gallery class
    """

    def __init__(self, directory, height):
        self._directory = directory
        self._height = height

        try:
            self._files = [x for x in sorted(os.listdir(
                directory)) if x.split('.')[-1].lower() in IMAGE_EXTS]
        except PermissionError:
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + directory + '" directory.')
        self._nfiles = len(self._files)

    def generate(self, number, file, next_file):
        """
        Generate XHTML docuement

        number    = Number of images
        file      = Image file
        next_file = Next image file
        """
        yield (
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        )
        yield (
            '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" '
            'lang="en">'
        )
        yield ''
        yield '<head>'
        yield '<title>' + self._directory + '/' + file + '</title>'
        yield (
            '<meta http-equiv="Content-Type" content="text/html; '
            'charset=utf-8"/>'
        )
        yield '</head>'
        yield (
            '<body bgcolor="#fffff1" text="#000000" link="#0000ff" '
            'vlink="#900090">'
        )
        yield ''
        yield '<table border="0" align="center">'
        yield '<tr>'
        yield '  <td valign="top">'
        yield '  (' + str(number+1) + '/' + str(self._nfiles) + ')'
        yield '  </td>'
        yield '  <td>'
        yield '    <a href="' + next_file.rsplit('.', 1)[0] + '.xhtml">'
        yield (
            '    <img src="' + file + '" height="' + str(self._height) +
            '"/></a>'
        )
        yield '  </td>'
        yield '  <td>'
        yield '  </td>'
        yield '</tr>'
        yield '</table>'
        yield ''
        yield '</body></html>'

    def create(self):
        """
        Create gallery
        """
        if self._files:
            directory_time = 0
            for i in range(self._nfiles):
                file = self._files[i]

                next_file = self._files[(i+1) % self._nfiles]

                xhtml_file = os.path.join(
                    self._directory,
                    file.rsplit('.', 1)[0]
                ) + '.xhtml'
                try:
                    with open(xhtml_file, 'w', newline='\n') as ofile:
                        for line in self.generate(i, file, next_file):
                            print(line, file=ofile)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + xhtml_file +
                        '" file.'
                    )

                file_time = file_mod.FileStat(
                    os.path.join(self._directory, file)).get_time()
                os.utime(xhtml_file, (file_time, file_time))
                directory_time = max(directory_time, file_time)

            os.utime(self._directory, (directory_time, directory_time))
            return directory_time

        return None


class Xhtml(object):
    """
    Xhtml class
    """

    def __init__(self, options):
        self._height = options.get_height()
        self._directory = options.get_directory()

    def _find(self, directory=''):
        if directory:
            directories = [directory]
        else:
            directories = []

        for file in glob.glob(os.path.join(directory, '*')):
            if os.path.isdir(file):
                directories.extend(self._find(file))
        return directories

    @staticmethod
    def generate(file_stats):
        """
        Generate XHTML index file

        file_stats = List of FileStat class objects
        """
        yield (
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
        )
        yield (
            '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" '
            'lang="en">'
        )
        yield ''
        yield '<head>'
        yield '<title>Photo Galleries</title>'
        yield (
            '<meta http-equiv="Content-Type" content="text/html; '
            'charset=utf-8"/>'
        )
        yield '</head>'
        yield (
            '<body bgcolor="#fffff1" text="#000000" link="#0000ff" '
            'vlink="#900090">'
        )
        yield ''
        for file_stat in file_stats:
            directory = file_stat.get_file()
            files = glob.glob(os.path.join(directory, '*.xhtml'))
            nfiles = len(files)
            xhtml_file = sorted(files)[0]
            yield '<a href="' + xhtml_file + '" target="_blank">'
            yield '{0:s} ({1:d})</a>'.format(directory, nfiles)
            yield '<br/>'
            yield ''
        yield '</body></html>'

    def create(self):
        """
        Create files
        """
        try:
            os.chdir(self._directory)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot change to "' + self._directory() +
                '" directory.'
            )

        file_stats = []
        for directory in self._find():
            gallery = Gallery(directory, self._height)
            if gallery.create():
                file_stats.append(file_mod.FileStat(directory))
        file_stats = sorted(
            file_stats,
            key=lambda s: s.get_time(),
            reverse=True
        )

        try:
            with open('index.xhtml', 'w', newline='\n') as ofile:
                for line in self.generate(file_stats):
                    print(line, file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "index.xhtml" file.')


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
    def run():
        """
        Start program
        """
        options = Options()

        Xhtml(options).create()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
