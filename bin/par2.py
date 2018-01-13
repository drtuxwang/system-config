#!/usr/bin/env python3
"""
Wrapper for "par2" command
"""

import glob
import os
import shutil
import signal
import sys

import command_mod
import file_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of file.
        """
        return self._files

    def get_par2(self):
        """
        Return par2 Command class object.
        """
        return self._par2

    def parse(self, args):
        """
        Parse arguments
        """
        self._par2 = command_mod.Command('par2', errors='stop')

        if len(args) == 1 or not os.path.exists(args[1]):
            self._par2.set_args(args[1:])
            subtask_mod.Exec(self._par2.get_cmdline()).run()

        self._par2.set_args(['c', '-n1', '-r1'])
        self._files = args[1:]


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

    @classmethod
    def _par2(cls, cmdline, files):
        for file in files:
            if os.path.isdir(file):
                cls._par2(cmdline, sorted(glob.glob(os.path.join(file, '*'))))
            elif os.path.isfile(file) and not file.endswith('.par2'):
                file_stat = file_mod.FileStat(file)
                file_time = file_stat.get_time()
                par_file = file + '.par2'
                if file_time != file_mod.FileStat(par_file).get_time():
                    size = file_stat.get_size() // 400 * 4 + 4
                    print('debugX1', size)
                    task = subtask_mod.Task(cmdline + ['-s' + str(size), file])
                    task.run()
                    if task.get_exitcode() == 0:
                        try:
                            shutil.move(file + '.vol0+1.par2', par_file)
                            os.utime(par_file, (file_time, file_time))
                        except OSError:
                            pass

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        cls._par2(options.get_par2().get_cmdline(), options.get_files())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
