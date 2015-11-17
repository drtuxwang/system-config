#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job execution.
"""

RELEASE = '2.6.3'

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal
import time

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._release = RELEASE
        if len(args) != 3 or args[1] not in ('-jobid', '-spawn'):
            raise SystemExit(sys.argv[0] +
                             ': Cannot be started manually. Please run "myqsd" command.')
        self._mode = args[1][1:]
        self._myqsdir = os.path.join(os.environ['HOME'], '.config',
                                     'myqs', syslib.info.getHostname())
        self._jobid = args[2]

    def getJobid(self):
        """
        Return job ID.
        """
        return self._jobid

    def getMode(self):
        """
        Return operation mode.
        """
        return self._mode

    def getMyqsdir(self):
        """
        Return myqs directory.
        """
        return self._myqsdir

    def getRelease(self):
        """
        Return release version.
        """
        return self._release


class Job(syslib.Dump):

    def __init__(self, options):
        self._myqsdir = options.getMyqsdir()
        self._jobid = options.getJobid()

        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        if options.getMode() == 'spawn':
            self._spawn(options)
        else:
            self._start(options)

    def _spawn(self, options):
        try:
            with open(os.path.join(self._myqsdir, self._jobid + '.r'), 'a',
                      newline='\n') as ofile:
                mypid = os.getpid()
                os.setpgid(mypid, mypid)  # New PGID
                pgid = os.getpgid(mypid)
                print('PGID=' + str(pgid) + '\nSTART=' + str(time.time()), file=ofile)
        except IOError:
            return

        try:
            with open(os.path.join(self._myqsdir, self._jobid + '.r'), errors='replace') as ifile:
                info = {}
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        info[line.split('=')[0]] = line.split('=', 1)[1]
        except IOError:
            return

        print('\nMyQS v' + options.getRelease() + ', My Queuing System batch job exec.\n')
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
            with open(command.getFile(), errors='replace') as ifile:
                line = ifile.readline().rstrip()
                if line == '#!/bin/sh':
                    sh = syslib.Command(file='/bin/sh')
                    command.setWrapper(sh)
        except IOError:
            pass

    def _start(self, options):
        try:
            with open(os.path.join(self._myqsdir, self._jobid + '.r'), errors='replace') as ifile:
                info = {}
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        info[line.split('=')[0]] = line.split('=', 1)[1]
        except IOError:
            return
        if os.path.isdir(info['DIRECTORY']):
            os.chdir(info['DIRECTORY'])
        else:
            os.chdir(os.environ['HOME'])
        renice = syslib.Command('renice', check=False)
        if renice.isFound():
            renice.setArgs(['100', str(os.getpid())])
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


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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

    def _windowsArgv(self):
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
