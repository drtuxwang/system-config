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
from typing import BinaryIO, List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self._output = None
        self.parse(sys.argv)

    def get_output(self) -> str:
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
            description='M3U8 streaming video downloader',
        )
        parser.add_argument(
            '-O',
            dest='output',
            default=None,
            help='MP4 output file name.'
        )
        parser.add_argument(
            'url',
            nargs=1,
            help='M3U8 video file URL.'
        )

        self._args = parser.parse_args(args)

        if not self._args.url[0].endswith('.m3u8'):
            raise SystemExit(
                sys.argv[0] + ": Wrong URL extension: " + self._args.output
            )
        if self._args.output:
            if not self._args.output.endswith('.mp4'):
                raise SystemExit(
                    sys.argv[0] + ": Wrong MP4 file extension: " +
                    self._args.output
                )
            self._output = self._args.output
        else:
            md5 = hashlib.md5()
            md5.update(self._args.url[0].encode())
            self._output = (
                os.path.basename(self._args.url[0]).rsplit('.', 1)[0] +
                '-' + md5.hexdigest()[:9] + '.mp4'
            )
        if os.path.isfile(self._output):
            print("{0:s}: already exists".format(self._output))
            raise SystemExit(0)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class VideoDownloader:
    """
    M38U video downloader.
    """
    def __init__(self, options: Options) -> None:
        self._output = options.get_output()
        self._url = options.get_url()

        self._wget = command_mod.Command('wget', errors='stop')
        self._directory = self._output + '.parts'
        self._m3u8_file = os.path.join(
            self._directory,
            os.path.basename(self._url),
        )

    def _write_resume(self) -> None:
        """
        Write download resume script.
        """
        script = (
            "#!/usr/bin/env bash",
            "cd ${0%/*}/..",
            'xrun "{0:s}" {1:s}'.format(self._output, self._url),
        )
        with open(self._m3u8_file + '-resume.sh', 'w', newline='\n') as ofile:
            for line in script:
                print(line, file=ofile)
        os.chmod(self._m3u8_file + '-resume.sh', int('755', 8))

    def get_m3u8(self) -> None:
        """
        Download M3U8 file.
        """
        if os.path.isfile(self._m3u8_file):
            return
        if not os.path.isdir(self._directory):
            os.makedirs(self._directory)
        self._write_resume()

        self._wget.set_args(['-O', self._m3u8_file, self._url])
        task = subtask_mod.Task(self._wget.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(1)

    def _get_urls(self) -> dict:
        """
        Return dict of containing URLs for video chunks.
        """
        base_url = os.path.dirname(self._url)

        chunks: dict = {}
        try:
            with open(self._m3u8_file) as ifile:
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
                sys.argv[0] + ": Cannot open file: " + self._m3u8_file
            ) from exception

        if len(chunks) == 0:
            raise SystemExit(
                sys.argv[0] + ": Cannot find chunks: " + self._m3u8_file)
        return chunks

    def _get_chunk(self, file: str, urls: List[str]) -> None:
        """
        Download chunk from available URLs.
        """
        for url in urls:
            if os.path.isfile(file + '.part'):
                os.remove(file + '.part')
            self._wget.set_args(['-O', file, url])
            task = subtask_mod.Task(self._wget.get_cmdline())
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
        nfiles = len(glob.glob(self._m3u8_file + '-c*.ts'))
        status_file = self._m3u8_file + '-status.txt'

        while nfiles != nchunks:
            for part, urls in sorted(chunks.items()):
                file = "{0:s}-c{1:05d}.ts".format(self._m3u8_file, part)
                if os.path.isfile(file):
                    continue

                self._get_chunk(file, urls)
                if os.path.isfile(file):
                    nfiles += 1
                    with open(status_file, 'w') as ofile:
                        print("{0:s}: {1:d}/{2:d}".format(
                            self._output,
                            nfiles,
                            nchunks,
                        ), file=ofile)

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
        chunk_files = sorted(glob.glob(self._m3u8_file + '-c*.ts'))
        full_file = self._m3u8_file + '-full.ts'
        with open(full_file, 'wb') as ofile:
            for file in chunk_files:
                print(file + "...")
                try:
                    with open(file, 'rb') as ifile:
                        self._copy(ifile, ofile)
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ": Cannot read file: " + file
                    ) from exception

        mp4_file = self._m3u8_file + '-full.mp4'
        if os.path.isfile(mp4_file):
            os.remove(mp4_file)
        ffmpeg = command_mod.Command('ffmpeg', errors='stop')
        ffmpeg.set_args([
            '-i',
            full_file,
            '-acodec',
            'copy',
            '-vcodec',
            'copy',
            mp4_file,
        ])
        task = subtask_mod.Task(ffmpeg.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(1)

        source_time = os.path.getmtime(self._m3u8_file)
        os.utime(mp4_file, (source_time, source_time))
        shutil.move(mp4_file, self._output)
        shutil.move(self._directory, self._output+'.full')
        print("{0:s}: generated from {1:d} chunks!".format(
            self._output,
            len(chunk_files),
        ))
        shutil.rmtree(self._output+'.full')


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
