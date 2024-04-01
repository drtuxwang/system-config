#!/usr/bin/env python3
"""
M3U8 streaming video downloader.
"""

import argparse
import glob
import hashlib
import os
import shutil
import signal
import sys
import time
from pathlib import Path
from typing import Any, BinaryIO, List

from command_mod import Command
from subtask_mod import Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_output(self) -> Path:
        """
        Return output file.
        """
        return self._output

    def get_url(self) -> str:
        """
        Return M3U8 file URL.
        """
        return self._args.url[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="M3U8 streaming video downloader",
        )
        parser.add_argument(
            '-O',
            dest='output',
            default=None,
            help="MP4 output file name.",
        )
        parser.add_argument(
            'url',
            nargs=1,
            help="M3U8 video file URL.",
        )

        self._args = parser.parse_args(args)

        if '.m3u8' not in self._args.url[0]:
            raise SystemExit(
                f"{sys.argv[0]}: Wrong URL extension: {self._args.output}",
            )

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.output:
            self._output = Path(self._args.output).with_suffix('.mp4')
        else:
            md5 = hashlib.md5()
            md5.update(self._args.url[0].encode())
            path = Path(self._args.url[0]).name
            self._output = Path(
                f"{path.rsplit('?', 1)[0].rsplit('.', 1)[0]}-"
                f"{md5.hexdigest()[:9]}.mp4"
            )
        if Path(self._output).is_file():
            print(f"{self._output}: already exists")
            raise SystemExit(0)


class VideoDownloader:
    """
    M38U video downloader.
    """
    def __init__(self, options: Options) -> None:
        self._output = options.get_output()
        self._url = options.get_url()

        self._wget = Command('wget', errors='stop')
        self._directory_path = Path(f'{self._output}.parts')
        self._m3u8_file = Path(self._directory_path, Path(self._url).name)

    def _write_resume(self) -> None:
        """
        Write download resume script.
        """
        script = (
            "#!/usr/bin/env bash",
            "cd ${0%/*}/..",
            f'xrun "{self._output}" {self._url}',
        )
        resume_file = Path(f'{self._m3u8_file}-resume.sh')
        with resume_file.open('w') as ofile:
            for line in script:
                print(line, file=ofile)
        resume_file.chmod(0o755)

    def get_m3u8(self) -> None:
        """
        Download M3U8 file.
        """
        if self._m3u8_file.is_file():
            return
        if not self._directory_path.is_dir():
            self._directory_path.mkdir(parents=True)
        self._write_resume()

        self._wget.set_args(['-O', self._m3u8_file, self._url])
        task = Task(self._wget.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(1)

    def _get_urls(self) -> dict:
        """
        Return dict of containing URLs for video chunks.
        """
        base_url = self._url.rsplit('/', 1)[0]

        chunks: dict = {}
        path = Path(self._m3u8_file)
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    line = line.strip()
                    if not line.startswith('#'):
                        url = '/'.join([base_url, line])
                        if '-chunk-' in line:
                            part = int(line.split('-chunk-')[1].split('.')[0])
                            chunks[part] = chunks.get(part, []) + [url]
                        else:
                            chunks[len(chunks)] = [url]
        except OSError as exception:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot open file: {path}",
            ) from exception

        if len(chunks) == 0:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot find chunks: {path}",
            )
        return chunks

    def _get_chunk(self, path: Path, urls: List[str]) -> None:
        """
        Download chunk from available URLs.
        """
        for url in urls:
            if Path(f'{path}.part').is_file():
                Path(f'{path}.part').unlink()
            self._wget.set_args(['-O', path, url])
            task = Task(self._wget.get_cmdline())
            task.run()
            if task.get_exitcode() == 0:
                return
        time.sleep(2)

    def get_parts(self) -> None:
        """
        Download video parts.
        """
        chunks = self._get_urls()
        nchunks = len(chunks)
        nfiles = len(glob.glob(f'{self._m3u8_file}-c*.ts'))
        status_file = Path(f'{self._m3u8_file}-status.txt')

        while nfiles != nchunks:
            for part, urls in sorted(chunks.items()):
                path = Path(f"{self._m3u8_file}-c{part:05d}.ts")
                if path.is_file():
                    continue

                self._get_chunk(path, urls)
                if path.is_file():
                    nfiles += 1
                    with status_file.open('w') as ofile:
                        print(
                            f"{self._output}: {nfiles}/{nchunks}",
                            file=ofile,
                        )

            time.sleep(10)

    @staticmethod
    def _copy(ifile: BinaryIO, ofile: BinaryIO) -> None:
        while True:
            chunk = ifile.read(131072)
            if not chunk:
                break
            ofile.write(chunk)

    def join(self) -> None:
        """
        Join video parts.
        """
        chunk_files = sorted(glob.glob(f'{self._m3u8_file}-c*.ts'))
        full_path = Path(f'{self._m3u8_file}-full.ts')
        with full_path.open('wb') as ofile:
            for path in [Path(x) for x in chunk_files]:
                print(f"{path}...")
                try:
                    with path.open('rb') as ifile:
                        self._copy(ifile, ofile)
                except OSError as exception:
                    raise SystemExit(
                        f"{sys.argv[0]}: Cannot read file: {path}",
                    ) from exception

        mp4_path = Path(f'{self._m3u8_file}-full.mp4')
        if mp4_path.is_file():
            mp4_path.unlink()
        ffmpeg = Command('ffmpeg', errors='stop')
        ffmpeg.set_args([
            '-i',
            full_path,
            '-acodec',
            'copy',
            '-vcodec',
            'copy',
            mp4_path,
        ])
        task = Task(ffmpeg.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(1)

        source_time = int(self._m3u8_file.stat().st_mtime)
        os.utime(mp4_path, (source_time, source_time))
        mp4_path.replace(self._output)
        Path(self._directory_path).replace(f'{self._output}.full')
        print(f"{self._output}: generated from {len(chunk_files)} chunks!")
        shutil.rmtree(f'{self._output}.full')


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
        if sys.version_info < (3, 9):
            def _readlink(file: Any) -> Path:
                return Path(os.readlink(file))
            Path.readlink = _readlink  # type: ignore

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        video = VideoDownloader(options)
        video.get_m3u8()
        video.get_parts()
        video.join()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
