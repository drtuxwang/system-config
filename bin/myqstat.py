#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job statistics.
"""

import argparse
import glob
import os
import signal
import sys
import time

import syslib

RELEASE = '2.7.1'

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._release = RELEASE

        self._parse_args(args[1:])

    def get_release(self):
        """
        Return release version.
        """
        return self._release

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release + ', My Queuing System batch job submission.')

        self._args = parser.parse_args(args)


class Stats(object):
    """
    Stats class
    """

    def __init__(self, options):
        hostname = syslib.info.get_hostname()
        print('\nMyQS', options.get_release(),
              ', My Queuing System batch job statistics on HOST "' + hostname + '".\n')
        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        self._myqsdir = os.path.join(os.environ['HOME'], '.config',
                                     'myqs', syslib.info.get_hostname())
        self._showjobs()
        self._myqsd()

    def _myqsd(self):
        lockfile = os.path.join(self._myqsdir, 'myqsd.pid')
        try:
            with open(lockfile, errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if syslib.Task().haspid(pid):
                        return
                    else:
                        os.remove(lockfile)
        except OSError:
            pass
        print('MyQS batch job scheduler not running. Run "myqsd" command.')

    def _showjobs(self):
        print('JOBID  QUEUENAME  JOBNAME                                     CPUS  STATE  TIME')
        jobids = []
        for file in glob.glob(os.path.join(self._myqsdir, '*.[qr]')):
            try:
                jobids.append(int(os.path.basename(file)[:-2]))
            except ValueError:
                pass
        for jobid in sorted(jobids):
            try:
                ifile = open(os.path.join(self._myqsdir, str(jobid) + '.q'), errors='replace')
            except OSError:
                try:
                    ifile = open(os.path.join(self._myqsdir, str(jobid) + '.r'), errors='replace')
                except OSError:
                    continue
                state = 'RUN'
            else:
                state = 'QUEUE'
            info = {}
            for line in ifile:
                line = line.strip()
                if '=' in line:
                    info[line.strip().split('=')[0]] = line.split('=', 1)[1]
            ifile.close()
            if 'NCPUS' in info:
                self._show_details(info, jobid, state)
        print()

    def _show_details(self, info, jobid, state):
        output = []
        if 'START' in info:
            try:
                etime = str(int((time.time()-float(info['START']))/60.))
                pgid = int(info['PGID'])
            except ValueError:
                etime = '0'
            else:
                if syslib.Task().haspgid(pgid):
                    if os.path.isdir(info['DIRECTORY']):
                        logfile = os.path.join(
                            info['DIRECTORY'], os.path.basename(info['COMMAND']) +
                            '.o' + str(jobid))
                    else:
                        logfile = os.path.join(
                            os.environ['HOME'], os.path.basename(info['COMMAND']) +
                            '.o' + str(jobid))
                    try:
                        with open(logfile, errors='replace') as ifile:
                            output = []
                            for line in ifile:
                                output = (output + [line.rstrip()])[-5:]
                    except OSError:
                        pass
                else:
                    state = 'STOP'
        else:
            etime = '-'
        print('{0:5d}  {1:9s}  {2:42s}  {3:>3s}   {4:5s} {5:>5s}'.format(
            jobid, info['QUEUE'], info['COMMAND'], info['NCPUS'], state, etime))
        for line in output:
            print(line)


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
            Stats(options)
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
