#!/usr/bin/env python3
"""
Generate 'index.xhtml' & 'index.fsum' files plus '.../fsum' cache files
"""

import glob
import logging
import os
import re
import shutil
import signal
import sys
from typing import List

import command_mod
import file_mod
import logging_mod
import subtask_mod

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


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

    @classmethod
    def _checksum(cls) -> None:
        fsum = command_mod.Command('fsum', errors='stop')
        files = glob.glob('*')
        if 'index.fsum' in files:
            files.remove('index.fsum')
            fsum.set_args(['-R', '-update=index.fsum'] + files)
        else:
            fsum.set_args(['-R'] + files)
        task = subtask_mod.Batch(fsum.get_cmdline())

        task.run()
        cls._write_fsums(task.get_output())

        task.run()
        time_new = 0
        try:
            lines = []
            if os.path.isfile('index.fsum'):
                with open('index.fsum', errors='replace') as ifile:
                    for line in ifile:
                        lines.append(line.rstrip('\r\n'))
                if lines == task.get_output():
                    return

            logger.info("Writing checksums: index.fsum")
            with open('index.fsum.part', 'w', newline='\n') as ofile:
                for line in task.get_output():
                    time_new = max(
                        time_new,
                        int(line.split(' ', 1)[0].rsplit('/', 1)[-1])
                    )
                    print(line, file=ofile)
            os.utime('index.fsum.part', (time_new, time_new))
            shutil.move('index.fsum.part', 'index.fsum')
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "index.fsum" file.'
            ) from exception

    @staticmethod
    def _checkfile(isbadfile: re.Pattern, directory: str = os.curdir) -> None:
        """
        Look for bad files like core dumps
        (don't followlinks & onerror do nothing)
        """
        error = False
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.abspath(os.path.join(root, file))
                if isbadfile.search(file):
                    print("Error: Found bad file:", file_path)
                    error = True
                try:
                    if os.path.getsize(file_path) == 0:
                        print("Error: Found zero size file:", file_path)
                        error = True
                except OSError:
                    print("Error: Found broken link:", file_path)
                    error = True
        if error:
            raise SystemExit(1)

    @staticmethod
    def _create_directory(directory: str) -> None:
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' +
                    directory + '" directory.'
                ) from exception

    @classmethod
    def _set_time(cls, directory: str) -> None:
        """
        Fix directory and symbolic link modified times.
        """
        files = [os.path.join(directory, x) for x in os.listdir(directory)]
        for file in files:
            if os.path.islink(file):
                link_stat = file_mod.FileStat(file, follow_symlinks=False)
                file_stat = file_mod.FileStat(file)
                file_time = file_stat.get_time()
                if file_time != link_stat.get_time():
                    os.utime(
                        file,
                        (file_time, file_time),
                        follow_symlinks=False,
                    )
            elif os.path.isdir(file):
                cls._set_time(file)

        if files:
            newest = file_mod.FileUtil.newest(files)
            file_stat = file_mod.FileStat(newest)
            file_time = file_stat.get_time()
            if file_time != file_mod.FileStat(directory).get_time():
                os.utime(directory, (file_time, file_time))

    @classmethod
    def _write_fsums(cls, lines: List[str]) -> None:
        fsums: dict = {}
        for line in lines:
            checksum, file = line.split('  ', 1)
            directory = os.path.dirname(file)
            if os.path.basename(directory) == '...':
                directory = os.path.dirname(directory)
                filename = os.path.basename(file)
                if filename == 'fsum':
                    continue
            else:
                filename = '../' + os.path.basename(file)
            if directory not in fsums:
                fsums[directory] = []
            fsums[directory].append(checksum + '  ' + filename)

        for directory in sorted(fsums):
            directory_3dot = os.path.join(directory, '...')
            cls._create_directory(directory_3dot)
            file = os.path.join(directory_3dot, 'fsum')

            time_new = 0
            try:
                lines = []
                if os.path.isfile(file):
                    with open(file, errors='replace') as ifile:
                        for line in ifile:
                            lines.append(line.rstrip('\r\n'))
                    if lines == fsums[directory]:
                        continue

                logger.info("Writing checksums: %s", file)
                with open(file+'.part', 'w', newline='\n') as ofile:
                    for line in fsums[directory]:
                        time_new = max(
                            time_new,
                            int(line.split(' ', 1)[0].rsplit('/', 1)[-1])
                        )
                        print(line, file=ofile)
                os.utime(file+'.part', (time_new, time_new))
                shutil.move(file+'.part', file)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + file + '" file.'
                ) from exception

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        isbadfile = re.compile(r'^core([.]\d+)?$')

        cls._checkfile(isbadfile)
        cls._checksum()
        cls._set_time(os.getcwd())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
