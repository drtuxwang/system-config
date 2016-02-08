#!/usr/bin/env python3
"""
Generate 'index.xhtml' & 'index.fsum' files plus '..fsum' cache files
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


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

    def _checksum(self):
        print('Generating "index.fsum"...')
        try:
            with open('index.fsum', 'a', newline='\n') as ofile:
                self._read_fsums(ofile, '')
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "index.fsum" file.')

        fsum = syslib.Command('fsum')
        files = glob.glob('*')
        if 'index.fsum' in files:
            files.remove('index.fsum')
            fsum.set_args(['-R', '-update=index.fsum'] + files)
        else:
            fsum.set_args(['-R'] + files)
        fsum.run(mode='batch')

        self._write_fsums(fsum.get_output())
        time_new = 0
        try:
            with open('index.fsum', 'w', newline='\n') as ofile:
                for line in fsum.get_output():
                    time_new = max(time_new, int(line.split(' ', 1)[0].rsplit('/', 1)[-1]))
                    print(line, file=ofile)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "index.fsum" file.')
        os.utime('index.fsum', (time_new, time_new))

    def _core_find(self, directory=''):
        for file in sorted(glob.glob(os.path.join(directory, '.*')) +
                           glob.glob(os.path.join(directory, '*'))):
            if not os.path.islink(file):
                if os.path.isdir(file):
                    self._core_find(file)
                elif os.path.basename(file) == 'core' or os.path.basename(file).startswith('core.'):
                    raise SystemExit(sys.argv[0] + ': Found "' + file + '" crash dump file.')

    def _read_fsums(self, ofile, directory):
        fsum = os.path.join(directory, '..fsum')
        if directory and os.listdir(directory) == ['..fsum']:
            try:
                os.remove(fsum)
            except OSError:
                pass
        else:
            try:
                with open(fsum, errors='replace') as ifile:
                    for line in ifile:
                        checksum, file = line.rstrip('\r\n').split('  ', 1)
                        print(checksum + '  ' + os.path.join(directory, file), file=ofile)
            except (OSError, ValueError):
                pass
            for file in glob.glob(os.path.join(directory, '*')):
                if os.path.isdir(file) and not os.path.islink(file):
                    self._read_fsums(ofile, file)

    @staticmethod
    def _write_fsums(lines):
        fsums = {}
        for line in lines:
            checksum, file = line.split('  ', 1)
            directory = os.path.dirname(file)
            if directory not in fsums:
                fsums[directory] = []
            fsums[os.path.dirname(file)].append(checksum + '  ' + os.path.basename(file))

        directories = {}
        for directory in sorted(fsums.keys()):
            depth = directory.count(os.sep)
            if depth not in directories:
                directories[depth] = [directory]
            directories[depth].append(directory)

        for depth in sorted(directories.keys(), reverse=True):
            for directory in directories[depth]:
                file = os.path.join(directory, '..fsum')
                time_new = 0
                try:
                    with open(file, 'w', newline='\n') as ofile:
                        for line in fsums[directory]:
                            time_new = max(time_new, int(line.split(' ', 1)[0].rsplit('/', 1)[-1]))
                            print(line, file=ofile)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" file.')
                os.utime(file, (time_new, time_new))
                if directory:
                    os.utime(directory, (time_new, time_new))

    def run(self):
        """
        Start program
        """
        self._core_find()
        self._checksum()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
