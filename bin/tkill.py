#!/usr/bin/env python3
"""
Kill tasks by process ID or name.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getForceFlag(self):
        """
        Return force flag.
        """
        return self._args.forceFlag

    def getKeyword(self):
        """
        Return process ID or keyword.
        """
        return self._args.task[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Kill tasks by process ID or name.')

        parser.add_argument('-f', dest='forceFlag', action='store_true',
                            help='Force termination of tasks.')

        parser.add_argument('task', nargs=1, metavar='pid|keyword', help='Process ID or keyword.')

        self._args = parser.parse_args(args)


class Kill:

    def __init__(self, options):
        pids = self._filter(options)
        self._ykill(options, pids)

    def _filter(self, options):
        task = syslib.Task()
        keyword = options.getKeyword()
        if keyword.isdigit():
            if task.haspid(int(keyword)):
                pids = [int(keyword)]
            else:
                pids = []
        else:
            pids = task.pname2pids('.*' + keyword + '.*')

        print('RUSER      PID  PPID  PGID PRI  NI TTY      MEMORY  CPUTIME     ELAPSED COMMAND')
        for pid in pids:
            process = task.getProcess(pid)
            print('{0:8s} {1:5d} {2:5d} {3:5d} {4:>3s} {5:>3s} {6:7s} {7:7d} {8:>8s} '
                  '{9:>11s} {10:s}'.format(
                      process['USER'].split()[0], pid, process['PPID'],
                      process['PGID'], process['PRI'], process['NICE'], process['TTY'],
                      process['MEMORY'], process['CPUTIME'], process['ETIME'], process['COMMAND']))
        print()
        return pids

    def _ykill(self, options, pids):
        task = syslib.Task()
        mypid = os.getpid()
        apids = task.getAncestorPids(mypid)
        for pid in pids:
            if pid == mypid:
                print('Process', pid, 'is my own process ID')
            elif pid in apids:
                print('Process', pid, 'is my ancestor process')
            else:
                if not options.getForceFlag():
                    answer = input('Kill process ' + str(pid) + ' (y/n): ')
                    if answer not in ('y', 'Y'):
                        continue
                task.killpids([pid])
                print('Process', pid, 'killed')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Kill(options)
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
