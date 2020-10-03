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

import command_mod
import logging_mod
import subtask_mod

# pylint: disable = invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable = invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


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

    def _checksum(self):

        fsum = command_mod.Command('fsum', errors='stop')
        files = glob.glob('*')
        if 'index.fsum' in files:
            files.remove('index.fsum')
            fsum.set_args(['-R', '-update=index.fsum'] + files)
        else:
            fsum.set_args(['-R'] + files)
        task = subtask_mod.Batch(fsum.get_cmdline())

        task.run()
        self._write_fsums(task.get_output())

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
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "index.fsum" file.')

    @staticmethod
    def _checkfile(isbadfile, directory=os.curdir):
        """
        Look for bad files like core dumps
        (don't followlinks & onerror do northing)
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
    def _create_directory(directory):
        if not os.path.isdir(directory):
            try:
                os.mkdir(directory)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' +
                    directory + '" directory.'
                )

    @classmethod
    def _write_fsums(cls, lines):
        fsums = {}
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
                with open(file, 'w', newline='\n') as ofile:
                    for line in fsums[directory]:
                        time_new = max(
                            time_new,
                            int(line.split(' ', 1)[0].rsplit('/', 1)[-1])
                        )
                        print(line, file=ofile)
                os.utime(file, (time_new, time_new))
                os.utime(directory, (time_new, time_new))
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + file + '" file.')

    def run(self):
        """
        Start program
        """
        isbadfile = re.compile(r'^core([.]\d+)?$')

        self._checkfile(isbadfile)
        self._checksum()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
