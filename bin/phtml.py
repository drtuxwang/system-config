#!/usr/bin/env python3
"""
Generate XHTML files to view pictures.
"""

import argparse
import glob
import os
import signal
import sys
from typing import Generator, List

import file_mod
import config_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_directory(self) -> str:
        """
        Return list of directory.
        """
        return self._args.directory[0]

    def get_height(self) -> int:
        """
        Return hieght in pixels.
        """
        return self._args.height

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Generate XHTML files to view pictures.",
        )

        parser.add_argument(
            '-height',
            type=int,
            default=600,
            help="Select picture height in pixels (default 600).",
        )
        parser.add_argument(
            'directory',
            nargs=1,
            help="Directory containing picture files.",
        )

        self._args = parser.parse_args(args)

        if self._args.height < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                'positive integer for picture height.',
            )
        if not os.path.isdir(self._args.directory[0]):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{self._args.directory[0]}" directory.',
            )

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Gallery:
    """
    Gallery class
    """

    def __init__(self, directory: str, height: int) -> None:
        self._directory = directory
        self._height = height
        images_extensions = config_mod.Config().get('image_extensions')

        try:
            self._files = [
                x
                for x in sorted(os.listdir(directory))
                if os.path.splitext(x)[1].lower() in images_extensions
            ]
        except PermissionError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{directory}" directory.',
            ) from exception
        self._nfiles = len(self._files)

    def generate(
        self,
        number: int,
        file: str,
        next_file: str,
    ) -> Generator[str, None, None]:
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
        yield f'<title>{self._directory}/{file}</title>'
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
        yield f'  ({number+1}/{self._nfiles})'
        yield '  </td>'
        yield '  <td>'
        yield f"    <a href=\"{next_file.rsplit('.', 1)[0]}.xhtml\">"
        yield f'    <img src="{file}" height="{self._height}"/></a>'
        yield '  </td>'
        yield '  <td>'
        yield '  </td>'
        yield '</tr>'
        yield '</table>'
        yield ''
        yield '</body></html>'

    def create(self) -> int:
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
                    with open(
                        xhtml_file,
                        'w',
                        encoding='utf-8',
                        newline='\n',
                    ) as ofile:
                        for line in self.generate(i, file, next_file):
                            print(line, file=ofile)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "{xhtml_file}" file.',
                    ) from exception

                file_time = file_mod.FileStat(
                    os.path.join(self._directory, file)).get_time()
                os.utime(xhtml_file, (file_time, file_time))
                directory_time = max(directory_time, file_time)

            os.utime(self._directory, (directory_time, directory_time))
            return directory_time

        return None


class Xhtml:
    """
    Xhtml class
    """

    def __init__(self, options: Options) -> None:
        self._height = options.get_height()
        self._directory = options.get_directory()

    def _find(self, directory: str = '') -> List[str]:
        if directory:
            directories = [directory]
        else:
            directories = []

        for file in glob.glob(os.path.join(directory, '*')):
            if os.path.isdir(file):
                directories.extend(self._find(file))
        return directories

    @staticmethod
    def generate(
        file_stats: List[file_mod.FileStat],
    ) -> Generator[str, None, None]:
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
            yield f'<a href="{xhtml_file}" target="_blank">'
            yield f'{directory} ({nfiles})</a>'
            yield '<br/>'
            yield ''
        yield '</body></html>'

    def create(self) -> None:
        """
        Create files
        """
        try:
            os.chdir(self._directory)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot change to '
                f'"{self._directory}" directory.',
            ) from exception

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
            with open(
                'index.xhtml',
                'w',
                encoding='utf-8',
                newline='\n',
            ) as ofile:
                for line in self.generate(file_stats):
                    print(line, file=ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create "index.xhtml" file.',
            ) from exception


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        Xhtml(options).create()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
