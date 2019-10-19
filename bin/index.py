#!/usr/bin/env python3
"""
Generate 'index.xhtml' & 'index.fsum' files plus '.../fsum' cache files
"""

import glob
import logging
import os
import re
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
        logger.info('Generating "index.fsum"')
        try:
            with open('index.fsum', 'a', newline='\n') as ofile:
                self._read_fsums(ofile, '')
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "index.fsum" file.')

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
        time_new = 0
        try:
            with open('index.fsum', 'w', newline='\n') as ofile:
                for line in task.get_output():
                    time_new = max(
                        time_new,
                        int(line.split(' ', 1)[0].rsplit('/', 1)[-1])
                    )
                    print(line, file=ofile)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "index.fsum" file.')
        os.utime('index.fsum', (time_new, time_new))

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

    def _read_fsums(self, ofile, directory):
        fsum = os.path.join(directory, '...', 'fsum')
        if directory and os.listdir(directory) == ['...']:
            try:
                os.remove(fsum)
            except OSError:
                pass
        else:
            try:
                with open(fsum, errors='replace') as ifile:
                    for line in ifile:
                        checksum, file = line.rstrip('\r\n').split('  ', 1)
                        print(
                            checksum + "  " + os.path.join(directory, file),
                            file=ofile
                        )
            except (OSError, ValueError):
                pass
            for file in glob.glob(os.path.join(directory, '*')):
                if os.path.isdir(file) and not os.path.islink(file):
                    self._read_fsums(ofile, file)

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
            if directory not in fsums:
                fsums[directory] = []
            fsums[os.path.dirname(file)].append(
                checksum + '  ' + os.path.basename(file))

        directories = {}
        for directory in sorted(fsums):
            depth = directory.count(os.sep)
            if depth not in directories:
                directories[depth] = [directory]
            directories[depth].append(directory)

        for depth in sorted(directories, reverse=True):
            for directory in directories[depth]:
                directory_3dot = os.path.join(directory, '...')
                cls._create_directory(directory_3dot)
                file = os.path.join(directory_3dot, 'fsum')
                time_new = 0
                try:
                    with open(file, 'w', newline='\n') as ofile:
                        for line in fsums[directory]:
                            time_new = max(
                                time_new,
                                int(line.split(' ', 1)[0].rsplit('/', 1)[-1])
                            )
                            print(line, file=ofile)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + file + '" file.')
                os.utime(file, (time_new, time_new))
                if directory:
                    os.utime(directory, (time_new, time_new))

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
