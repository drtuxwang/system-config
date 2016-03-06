#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job execution.
"""

import glob
import os
import signal
import socket
import sys
import time

import command_mod
import subtask_mod

RELEASE = '2.7.3'

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._release = RELEASE
        self._args = None
        self.parse(sys.argv)

    def get_jobid(self):
        """
        Return job ID.
        """
        return self._jobid

    def get_mode(self):
        """
        Return operation mode.
        """
        return self._mode

    def get_myqsdir(self):
        """
        Return myqs directory.
        """
        return self._myqsdir

    def get_release(self):
        """
        Return release version.
        """
        return self._release

    def parse(self, args):
        """
        Parse arguments
        """
        if len(args) != 3 or args[1] not in ('-jobid', '-spawn'):
            raise SystemExit(sys.argv[0] +
                             ': Cannot be started manually. Please run "myqsd" command.')
        self._mode = args[1][1:]
        self._myqsdir = os.path.join(
            os.environ['HOME'], '.config', 'myqs', socket.gethostname().split('.')[0].lower())
        self._jobid = args[2]


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

    @staticmethod
    def _get_command(file):
        if os.path.isfile(file):
            return command_mod.CommandFile(os.path.abspath(file))
        else:
            return command_mod.Command(file, errors='stop')

    def _spawn(self, options):
        try:
            with open(os.path.join(self._myqsdir, self._jobid + '.r'), 'a',
                      newline='\n') as ofile:
                mypid = os.getpid()
                os.setpgid(mypid, mypid)  # New PGID
                pgid = os.getpgid(mypid)
                print('PGID=' + str(pgid) + '\nSTART=' + str(time.time()), file=ofile)
        except OSError:
            return

        try:
            with open(os.path.join(self._myqsdir, self._jobid + '.r'), errors='replace') as ifile:
                info = {}
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        info[line.split('=')[0]] = line.split('=', 1)[1]
        except OSError:
            return

        print('\nMyQS v' + options.get_release() + ', My Queuing System batch job exec.\n')
        print('MyQS JOBID  =', self._jobid)
        print('MyQS QUEUE  =', info['QUEUE'])
        print('MyQS NCPUS  =', info['NCPUS'])
        print('MyQS PGID   =', pgid)
        print('MyQS START  =', time.strftime('%Y-%m-%d-%H:%M:%S'))
        print('-'*80)
        sys.stdout.flush()
        os.environ['PATH'] = info['PATH']
        command = self._get_command(info['COMMAND'])
        self._sh(command)
        subtask_mod.Exec(command.get_cmdline()).run()

    @staticmethod
    def _sh(command):
        try:
            with open(command.get_file(), errors='replace') as ifile:
                line = ifile.readline().rstrip()
                if line == '#!/bin/sh':
                    command.set_args(['/bin/sh'] + command.get_cmdline())
        except OSError:
            pass

    def _start(self):
        try:
            with open(os.path.join(self._myqsdir, self._jobid + '.r'), errors='replace') as ifile:
                info = {}
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        info[line.split('=')[0]] = line.split('=', 1)[1]
        except OSError:
            return
        if os.path.isdir(info['DIRECTORY']):
            os.chdir(info['DIRECTORY'])
        else:
            os.chdir(os.environ['HOME'])
        renice = command_mod.Command('renice', errors='ignore')
        if renice.is_found():
            renice.set_args(['100', str(os.getpid())])
            subtask_mod.Batch(renice.get_cmdline()).run()
        myqexec = command_mod.CommandFile(__file__, args=['-spawn', self._jobid])
        subtask_mod.Task(myqexec.get_cmdline()).run()
        print('-'*80)
        print('MyQS FINISH =', time.strftime('%Y-%m-%d-%H:%M:%S'))
        time.sleep(1)
        try:
            os.remove(os.path.join(self._myqsdir, self._jobid + '.r'))
        except OSError:
            pass

    def run(self):
        """
        Start program
        """
        options = Options()

        self._myqsdir = options.get_myqsdir()
        self._jobid = options.get_jobid()

        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        if options.get_mode() == 'spawn':
            self._spawn(options)
        else:
            self._start()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
