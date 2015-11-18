#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job scheduler daemon
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


class Options:

    def __init__(self, args):
        self._release = RELEASE

        self._parseArgs(args[1:])

        self._myqsdir = os.path.join(os.environ['HOME'], '.config', 'myqs',
                                     syslib.info.getHostname())

    def getDaemonFlag(self):
        """
        Return daemon flag.
        """
        return self._args.daemonFlag

    def getMyqsdir(self):
        """
        Return myqs directory.
        """
        return self._myqsdir

    def getSlots(self):
        """
        Return CPU core slots.
        """
        return self._args.slots[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release + ', My Queuing System batch scheduler daemon.')

        parser.add_argument(
            '-daemon', dest='daemonFlag', action='store_true', help='Start batch job daemon.')

        parser.add_argument(
            'slots', nargs=1, type=int, help='The maximum number of CPU execution slots to create.')

        self._args = parser.parse_args(args)

        if self._args.slots[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'the number of slots.')


class Lock:

    def __init__(self, file):
        self._file = file
        self._pid = -1
        try:
            with open(self._file, errors='replace') as ifile:
                try:
                    self._pid = int(ifile.readline().strip())
                except (IOError, ValueError):
                    pass
        except IOError:
            pass

    def check(self):
        return syslib.Task().haspid(self._pid)

    def create(self):
        try:
            with open(self._file, 'w', newline='\n') as ofile:
                print(os.getpid(), file=ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' +
                             self._file + '" MyQS scheduler lock file.')
        time.sleep(1)
        try:
            with open(self._file, errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (IOError, ValueError):
                    raise SystemExit(0)
                else:
                    if not syslib.Task().haspid(os.getpid()):
                        raise SystemExit(sys.argv[0] + ": Cannot obtain MyQS scheduler lock file.")
        except IOError:
            return

    def remove(self):
        syslib.Task().killpids([self._pid])
        try:
            os.remove(self._file)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot remove "' + self._file + '" lock file.')


class Daemon:

    def __init__(self, options):
        self._myqsdir = options.getMyqsdir()
        self._slots = options.getSlots()

        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        if options.getDaemonFlag():
            self._schedulerDaemon(options)
        else:
            self._startDaemon(options)

    def _restart(self, options):
        for file in sorted(glob.glob(os.path.join(self._myqsdir, '*.r')),
                           key=lambda s: os.path.basename(s)[-2]):
            try:
                with open(os.path.join(file), errors='replace') as ifile:
                    info = {}
                    for line in ifile:
                        line = line.strip()
                        if '=' in line:
                            info[line.split('=')[0]] = line.split('=', 1)[1]
            except IOError:
                continue
            if 'PGID' in info:
                try:
                    pgid = int(info['PGID'])
                except ValueError:
                    pass
                if not syslib.Task().haspgid(pgid):
                    jobid = os.path.basename(file)[:-2]
                    print('Batch job with jobid "' + jobid +
                          '" being requeued after system restart...')
                    os.rename(file, file[:-2] + '.q')

    def _scheduleJob(self, options):
        running = 0
        for file in glob.glob(os.path.join(self._myqsdir, '*.r')):
            try:
                with open(file, errors='replace') as ifile:
                    info = {}
                    for line in ifile:
                        line = line.strip()
                        if '=' in line:
                            info[line.split('=')[0]] = line.split('=', 1)[1]
            except IOError:
                continue
            if 'PGID' in info:
                if not syslib.Task().haspgid(int(info['PGID'])):
                    time.sleep(0.5)
                    try:
                        os.remove(file)
                    except OSError:
                        continue
            if 'NCPUS' in info:
                try:
                    running += int(info['NCPUS'])
                except ValueError:
                    pass

        free = self._slots - running
        if free > 0:
            for queue in ('express', 'normal'):
                for file in sorted(glob.glob(os.path.join(self._myqsdir, '*.q')),
                                   key=lambda s: int(os.path.basename(s)[:-2])):
                    try:
                        with open(file, errors='replace') as ifile:
                            info = {}
                            for line in ifile:
                                line = line.strip()
                                if '=' in line:
                                    info[line.split('=')[0]] = line.split('=', 1)[1]
                    except IOError:
                        continue
                    if 'QUEUE' in info:
                        if info['QUEUE'] == queue:
                            if 'NCPUS' in info:
                                if free >= int(info['NCPUS']):
                                    jobid = os.path.basename(file)[:-2]
                                    if os.path.isdir(info['DIRECTORY']):
                                        logfile = os.path.join(info['DIRECTORY'], os.path.basename(
                                            info['COMMAND']) + '.o' + jobid)
                                    else:
                                        logfile = os.path.join(os.environ['HOME'], os.path.basename(
                                            info['COMMAND']) + '.o' + jobid)
                                    try:
                                        os.rename(file, file[:-2] + '.r')
                                    except OSError:
                                        continue
                                    myqexec = syslib.Command('myqexec', args=['-jobid', jobid])
                                    myqexec.run(logfile=logfile, mode='daemon')
                                    return

    def _schedulerDaemon(self, options):
        Lock(os.path.join(self._myqsdir, 'myqsd.pid')).create()
        while True:
            self._scheduleJob(options)
            time.sleep(2)

    def _startDaemon(self, options):
        if not os.path.isdir(self._myqsdir):
            try:
                os.makedirs(self._myqsdir)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot created "' +
                                 self._myqsdir + '" directory.')
        lock = Lock(os.path.join(self._myqsdir, 'myqsd.pid'))
        if lock.check():
            print('Stopping MyQS batch job scheduler...')
            lock.remove()
        else:
            self._restart(options)
        print('Starting MyQS batch job scheduler...')
        myqsd = syslib.Command(file=__file__, args=['-daemon', str(self._slots)])
        myqsd.run(mode='daemon')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Daemon(options)
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
