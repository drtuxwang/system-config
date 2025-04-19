#!/usr/bin/env python3
"""
Generate XHTML files to view images.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import Generator, List

from config_mod import Config
from file_mod import FileStat


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
            description="Generate XHTML files to view images.",
        )

        parser.add_argument(
            '-height',
            type=int,
            default=600,
            help="Select image height in pixels (default 600).",
        )
        parser.add_argument(
            'directory',
            nargs=1,
            help="Directory containing image files.",
        )

        self._args = parser.parse_args(args)

        if self._args.height < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a '
                'positive integer for image height.',
            )
        if not Path(self._args.directory[0]).is_dir():
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

    def __init__(self, path: Path, height: int) -> None:
        self._path = path
        self._height = height
        images_extensions = Config().get('image_extensions')

        try:
            self._files = [
                str(x.name)
                for x in path.iterdir()
                if x.suffix.lower() in images_extensions
            ]
        except PermissionError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot open "{path}" directory.',
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
        yield f'<title>{self._path}/{file}</title>'
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

                xhtml_file = Path(self._path, file).with_suffix('.xhtml')
                try:
                    with xhtml_file.open('w') as ofile:
                        for line in self.generate(i, file, next_file):
                            print(line, file=ofile)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "{xhtml_file}" file.',
                    ) from exception

                file_time = int(Path(self._path, file).stat().st_mtime)
                os.utime(xhtml_file, (file_time, file_time))
                directory_time = max(directory_time, file_time)

            os.utime(self._path, (directory_time, directory_time))
            return directory_time

        return None


class Xhtml:
    """
    Xhtml class
    """

    def __init__(self, options: Options) -> None:
        self._height = options.get_height()
        self._path = Path(options.get_directory())

    def _find(self, directory_path: Path = None) -> List[Path]:
        if directory_path:
            paths = [directory_path]
        else:
            paths = []

        for path in directory_path.glob('*'):
            if path.is_dir():
                paths.extend(self._find(path))
        return paths

    @staticmethod
    def generate(
        file_stats: List[FileStat],
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
            paths = list(Path(directory).glob('*.xhtml'))
            nfiles = len(paths)
            path = sorted(paths)[0]
            yield f'<a href="{path}" target="_blank">'
            yield f'{directory} ({nfiles})</a>'
            yield '<br/>'
            yield ''
        yield '</body></html>'

    def create(self) -> None:
        """
        Create files
        """
        try:
            os.chdir(self._path)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot change to "{self._path}" directory.',
            ) from exception

        file_stats = []
        for path in self._find():
            gallery = Gallery(path, self._height)
            if gallery.create():
                file_stats.append(FileStat(path))
        file_stats = sorted(
            file_stats,
            key=lambda s: s.get_mtime(),
            reverse=True
        )

        try:
            with Path('index.xhtml').open('w') as ofile:
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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

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
