#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job submission.
"""

RELEASE = '2.6.3'

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal
import time

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._release = RELEASE

        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getNcpus(self):
        """
        Return number of CPU slots.
        """
        return self._args.ncpus[0]

    def getQueue(self):
        """
        Return queue name.
        """
        return self._args.queue[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release + ', My Queuing System batch job submission.')

        parser.add_argument('-n', nargs=1, type=int, dest='ncpus', default=[1],
                            help='Select CPU core slots to reserve for job. Default is 1.')
        parser.add_argument('-q', nargs=1, dest='queue', default=['normal'],
                            help='Select "normal" or "express" queue. Default is "normal".')

        parser.add_argument('files', nargs='+', metavar='batch.sh', help='Batch job file.')

        self._args = parser.parse_args(args)

        if self._args.ncpus[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'the number of cpus.')
        elif self._args.queue[0] not in ('normal', 'express'):
            raise SystemExit(sys.argv[0] + ': Cannot submit to non-existent queue "' +
                             self._args.queue[0] + '".')


class Submit(syslib.Dump):

    def __init__(self, options):
        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        self._myqsdir = os.path.join(os.environ['HOME'], '.config',
                                     'myqs', syslib.info.getHostname())
        if not os.path.isdir(self._myqsdir):
            try:
                os.makedirs(self._myqsdir)
                os.chmod(self._myqsdir, int('700', 8))
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                 self._myqsdir + '" MyQS directory.')
        lockfile = self._lock()
        self._submit(options)
        os.remove(lockfile)
        self._myqsd()

    def _lastjob(self):
        lastjob = os.path.join(self._myqsdir, 'myqs.last')
        if os.path.isfile(lastjob):
            try:
                with open(lastjob, errors='replace') as ifile:
                    try:
                        jobid = int(ifile.readline().strip()) + 1
                    except (IOError, ValueError):
                        jobid = 1
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + lastjob + '" MyQS lastjob file.')
            if jobid > 32767:
                jobid = 1
        else:
            jobid = 1
        try:
            with open(lastjob, 'w', newline='\n') as ofile:
                print(jobid, file=ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot update "' + lastjob + '" MyQS lastjob file.')
        return jobid

    def _lock(self):
        while True:
            lockfile = os.path.join(self._myqsdir, 'myqsub.pid')
            if os.path.isfile(lockfile):
                try:
                    with open(lockfile, errors='replace') as ifile:
                        try:
                            pid = int(ifile.readline().strip())
                        except (IOError, ValueError):
                            pass
                        else:
                            if not syslib.Task().haspid(pid):
                                os.remove(lockfile)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' +
                                     lockfile + '" MyQS lock file.')
            if not os.path.isfile(lockfile):
                try:
                    with open(lockfile, 'w', newline='\n') as ofile:
                        print(os.getpid(), file=ofile)
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                     lockfile + '" MyQS lock file.')
                return lockfile
            time.sleep(1)

    def _myqsd(self):
        lockfile = os.path.join(self._myqsdir, 'myqsd.pid')
        try:
            with open(lockfile, errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (IOError, ValueError):
                    pass
                else:
                    if syslib.Task().haspid(pid):
                        return
                    else:
                        os.remove(lockfile)
        except IOError:
            pass
        print('MyQS batch job scheduler not running. Run "myqsd" command.')

    def _submit(self, options):
        tmpfile = os.path.join(self._myqsdir, 'newjob.tmp')
        queue = options.getQueue()
        ncpus = options.getNcpus()

        for file in options.getFiles():
            if not os.path.isfile(file):
                print('MyQS cannot find "' + file + '" batch file.')
                return
            jobid = self._lastjob()
            try:
                with open(tmpfile, 'w', newline='\n') as ofile:
                    print('COMMAND=' + file, file=ofile)
                    print('DIRECTORY=' + os.getcwd(), file=ofile)
                    print('PATH=' + os.environ['PATH'], file=ofile)
                    print('QUEUE=' + queue, file=ofile)
                    print('NCPUS=' + str(ncpus), file=ofile)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + tmpfile + '" temporary file.')
            os.rename(tmpfile, os.path.join(self._myqsdir, str(jobid) + '.q'))
            print('Batch job with jobid', jobid, 'has been submitted into MyQS.')
            time.sleep(0.5)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Submit(options)
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
