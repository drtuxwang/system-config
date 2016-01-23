#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job execution.
"""

import glob
import os
import signal
import sys
import time

import syslib

RELEASE = '2.7.1'

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._release = RELEASE
        if len(args) != 3 or args[1] not in ('-jobid', '-spawn'):
            raise SystemExit(sys.argv[0] +
                             ': Cannot be started manually. Please run "myqsd" command.')
        self._mode = args[1][1:]
        self._myqsdir = os.path.join(os.environ['HOME'], '.config',
                                     'myqs', syslib.info.get_hostname())
        self._jobid = args[2]

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


class Job(object):
    """
    Job class
    """

    def __init__(self, options):
        self._myqsdir = options.get_myqsdir()
        self._jobid = options.get_jobid()

        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        if options.get_mode() == 'spawn':
            self._spawn(options)
        else:
            self._start()

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
        if os.path.isfile(info['COMMAND']):
            command = syslib.Command(file=os.path.abspath(info['COMMAND']))
        else:
            command = syslib.Command(info['COMMAND'])
        self._sh(command)
        command.run(mode='exec')

    def _sh(self, command):
        try:
            with open(command.get_file(), errors='replace') as ifile:
                line = ifile.readline().rstrip()
                if line == '#!/bin/sh':
                    shell = syslib.Command(file='/bin/sh')
                    command.set_wrapper(shell)
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
        renice = syslib.Command('renice', check=False)
        if renice.is_found():
            renice.set_args(['100', str(os.getpid())])
            renice.run(mode='batch')
        myqexec = syslib.Command(file=__file__, args=['-spawn', self._jobid])
        myqexec.run()
        print('-'*80)
        print('MyQS FINISH =', time.strftime('%Y-%m-%d-%H:%M:%S'))
        time.sleep(1)
        try:
            os.remove(os.path.join(self._myqsdir, self._jobid + '.r'))
        except OSError:
            pass


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Job(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
