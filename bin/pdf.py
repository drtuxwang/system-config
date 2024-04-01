#!/usr/bin/env python3
"""
Create PDF from text/images/postscript/PDF/ODF files.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from config_mod import Config
from file_mod import FileUtil
from subtask_mod import Batch, Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archive(self) -> str:
        """
        Return PDF archive file.
        """
        return self._archive

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Create PDF file from text/images/"
            "postscript/PDF files.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Text/images/postscript/PDF file. A target ".pdf" file can '
            'be given as the first file.',
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.files[0].endswith('.pdf'):
            self._archive = self._args.files[0]
            self._files = self._args.files[1:]
            if self._archive in self._files:
                raise SystemExit(
                    f"{sys.argv[0]}: The input and "
                    "output files must be different.",
                )
        else:
            self._archive = ''
            self._files = self._args.files


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            self._tempfiles: List[str] = []
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

    def __del__(self) -> None:
        for file in self._tempfiles:
            try:
                os.remove(file)
            except OSError:
                pass

    def _image(self, path: Path) -> str:
        for command in ('identify', 'convert'):
            if command not in self._cache:
                self._cache[command] = Command(command, errors='stop')

        # Get size
        identify = self._cache['identify']
        task = Batch(identify.get_cmdline() + [path])
        task.run(pattern=f'^{path} [^ ]+ \\d+x\\d+ ', error2output=True)
        if not task.has_output():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" image file.',
            )
        size = task.get_output()[0].split()[2]
        xsize, ysize = size.split('x')

        convert = self._cache['convert']
        cmdline = convert.get_cmdline() + [
            '-strip',
            '-page',
            'a4',
            '-density',
            '72',
        ]
        if 'page' in path.name:
            info = f'Page IMAGE file "{path}"'
        elif size in ('2480x3508', '3508x2480', '1240x1754', '1754x1240'):
            info = f'A4 IMAGE file "{path}"'  # A4 300/150dpi
        else:
            cmdline.extend(['-border', '30', '-bordercolor', 'white'])
            info = f'IMAGE file "{path}" with margin'
        if int(xsize) > int(ysize):
            cmdline.extend(['-rotate', '270'])
        cmdline.extend([path, f'pdf:{self._tmpfile}'])

        task = Batch(cmdline)
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )
        return info

    def _postscript(self, path: Path) -> str:
        try:
            with path.open('rb') as ifile:
                path_new = Path(self._tmpfile)
                try:
                    with path_new.open('wb') as ofile:
                        for line in ifile:
                            ofile.write(line.rstrip(b"\r\n\x04") + b"\n")
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create '
                        f'"{path_new}" temporary file.',
                    ) from exception
                self._postscript_fix(path_new)
                return f'Postscript file "{path}"'
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" postscript file.',
            ) from exception

    def _postscript_fix(self, path: Path) -> None:
        scaling = None
        try:
            with Path(self._tmpfile).open(errors='replace') as ifile:
                for line in ifile:
                    if '/a3 setpagesize' in line:
                        scaling = 0.7071
                        break
        except OSError:
            pass
        if scaling:
            with path.open(errors='replace') as ifile:
                path_new = Path(f'{path}.part')
                with path_new.open('w') as ofile:
                    for line in ifile:
                        line = line.rstrip('\n')
                        if line.endswith(' setpagesize'):
                            columns = line.split()
                            columns[2] = '/a4'
                            line = ' '.join(columns)
                        elif line.endswith(' scale'):
                            xsize, ysize, _ = line.split()
                            line = (
                                f'{float(xsize) * scaling:6.4f} '
                                f'{float(ysize) * scaling:6.4f} scale'
                            )
                        print(line, file=ofile)
            path_new.replace(path)

    def _soffice(self, path: Path) -> str:
        path_tmp = Path(self._tmpfile).parent
        if 'soffice' not in self._cache:
            self._cache['soffice'] = Command(
                'soffice',
                args=[
                    '--headless',
                    '--convert-to',
                    'pdf',
                    '-outdir',
                    path_tmp,
                ],
                errors='stop',
            )
        soffice = self._cache['soffice']

        task = Batch(soffice.get_cmdline() + [path.name])
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )
        Path(path_tmp, path.name).with_suffix('.pdf').replace(self._tmpfile)
        return f'LibreOffice file "{path}"'

    def _paps(self, path: Path) -> str:
        if 'papss' not in self._cache:
            self._cache['paps'] = Command('paps', errors='stop')
            self._cache['paps'].set_args([
                '--paper=A4',
                '--header',
                '--left-margin=36',
                '--right-margin=36',
                '--font=Monospace 8.670',
            ])
            self._cache['ps2pdf'] = Command(
                'ps2pdf',
                args=['-'],
                errors='stop',
            )
        paps = self._cache['paps']
        ps2pdf = self._cache['ps2pdf']

        task = Batch(paps.get_cmdline() + [path, '|'] + ps2pdf.get_cmdline())
        task.run(file=self._tmpfile)
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )
        return f'UTF-8 text file "{path}" with 100 columns'

    def run(self) -> int:
        """
        Start program
        """
        options = Options()
        self._cache: dict = {}

        tmpdir = FileUtil.tmpdir('.cache')
        tmp_path = Path(tmpdir, f'pdf.tmp{os.getpid()}')
        command = Command('gs', errors='stop')
        command.set_args([
            '-q',
            '-dNOPAUSE',
            '-dBATCH',
            '-dSAFER',
            '-sDEVICE=pdfwrite',
            '-sPAPERSIZE=a4',
        ])

        images_extensions = Config().get('image_extensions')

        args: list = [
            f'-sOutputFile={options.get_archive()}',
            '-c',
            '3000000',
            'setvmthreshold',
        ]
        for path in [Path(x) for x in options.get_files()]:
            if not options.get_archive():
                args = [
                    f"-sOutputFile={path.with_suffix('.pdf')}",
                    '-c',
                    '3000000',
                    'setvmthreshold',
                ]
            if not path.is_file():
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{path}" file.')
            ext = path.suffix.lower()
            if ext == '.pdf':
                info = f'PDF file {path}'
                args.extend(['-f', path])
            else:
                self._tmpfile = f'{tmp_path}{len(self._tempfiles) + 1}'
                if ext in images_extensions:
                    info = self._image(path)
                    self._tempfiles.append(self._tmpfile + '.jpg')
                elif ext in ('ps', 'eps'):
                    info = self._postscript(path)
                elif ext == '.odt':
                    info = self._soffice(path)
                else:
                    info = self._paps(path)
                self._tempfiles.append(self._tmpfile)
                args.extend(['-f', self._tmpfile])
            if not options.get_archive():
                Task(command.get_cmdline() + args).run()
            print("Packing", info)
        if options.get_archive():
            Task(command.get_cmdline() + args).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
