#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job scheduler daemon
"""

import argparse
import glob
import os
import shutil
import signal
import socket
import sys
import time

import command_mod
import subtask_mod
import task_mod

RELEASE = '2.7.8'

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._release = RELEASE
        self._args = None
        self.parse(sys.argv)

    def get_daemon_flag(self):
        """
        Return daemon flag.
        """
        return self._args.daemon_flag

    def get_myqsdir(self):
        """
        Return myqs directory.
        """
        return self._myqsdir

    def get_slots(self):
        """
        Return CPU core slots.
        """
        return self._args.slots[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release +
            ', My Queuing System batch scheduler daemon.'
        )

        parser.add_argument(
            '-daemon',
            dest='daemon_flag',
            action='store_true',
            help='Start batch job daemon.'
        )
        parser.add_argument(
            'slots',
            nargs=1,
            type=int,
            help='The maximum number of CPU execution slots to create.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._myqsdir = os.path.join(
            os.environ['HOME'],
            '.config',
            'myqs',
            socket.gethostname().split('.')[0].lower()
        )

        if self._args.slots[0] < 1:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'the number of slots.'
            )


class Lock(object):
    """
    Lock class
    """

    def __init__(self, file):
        self._file = file
        self._pid = -1
        try:
            with open(self._file, errors='replace') as ifile:
                try:
                    self._pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
        except OSError:
            pass

    def check(self):
        """
        Return True if lock exists
        """
        return task_mod.Tasks.factory().haspid(self._pid)

    def create(self):
        """
        Create lock file
        """
        try:
            with open(self._file, 'w', newline='\n') as ofile:
                print(os.getpid(), file=ofile)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' +
                             self._file + '" MyQS scheduler lock file.')
        time.sleep(1)
        try:
            with open(self._file, errors='replace') as ifile:
                try:
                    int(ifile.readline().strip())
                except (OSError, ValueError):
                    raise SystemExit(0)
                else:
                    if not task_mod.Tasks.factory().haspid(os.getpid()):
                        raise SystemExit(
                            sys.argv[0] +
                            ": Cannot obtain MyQS scheduler lock file."
                        )
        except OSError:
            return

    def remove(self):
        """
        Remove lock file
        """
        task_mod.Tasks.factory().killpids([self._pid])
        try:
            os.remove(self._file)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot remove "' + self._file +
                '" lock file.'
            )


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

    def _restart(self):
        for file in sorted(glob.glob(os.path.join(self._myqsdir, '*.r')),
                           key=lambda s: os.path.basename(s)[-2]):
            try:
                with open(os.path.join(file), errors='replace') as ifile:
                    info = {}
                    for line in ifile:
                        line = line.strip()
                        if '=' in line:
                            info[line.split('=')[0]] = line.split('=', 1)[1]
            except OSError:
                continue
            if 'PGID' in info:
                try:
                    pgid = int(info['PGID'])
                except ValueError:
                    pass
                if not task_mod.Tasks.factory().haspgid(pgid):
                    jobid = os.path.basename(file)[:-2]
                    print('Batch job with jobid "' + jobid +
                          '" being requeued after system restart...')
                    shutil.move(file, file[:-2] + '.q')

    def _schedule_job(self):
        running = 0
        for file in glob.glob(os.path.join(self._myqsdir, '*.r')):
            try:
                with open(file, errors='replace') as ifile:
                    info = {}
                    for line in ifile:
                        line = line.strip()
                        if '=' in line:
                            info[line.split('=')[0]] = line.split('=', 1)[1]
            except OSError:
                continue
            if 'PGID' in info:
                if not task_mod.Tasks.factory().haspgid(int(info['PGID'])):
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

        free_slots = self._slots - running
        if free_slots > 0:
            self._attempt(free_slots)

    def _attempt(self, free_slots):
        for queue in ('express', 'normal'):
            for file in sorted(glob.glob(os.path.join(self._myqsdir, '*.q')),
                               key=lambda s: int(os.path.basename(s)[:-2])):
                try:
                    with open(file, errors='replace') as ifile:
                        info = {}
                        for line in ifile:
                            line = line.strip()
                            if '=' in line:
                                info[line.split('=')[0]] = (
                                    line.split('=', 1)[1])
                except OSError:
                    continue
                if 'QUEUE' in info:
                    if info['QUEUE'] == queue:
                        if 'NCPUS' in info:
                            if free_slots >= int(info['NCPUS']):
                                jobid = os.path.basename(file)[:-2]
                                if os.path.isdir(info['DIRECTORY']):
                                    logfile = os.path.join(
                                        info['DIRECTORY'],
                                        os.path.basename(info['COMMAND']) +
                                        '.o' + jobid
                                    )
                                else:
                                    logfile = os.path.join(
                                        os.environ['HOME'],
                                        os.path.basename(info['COMMAND']) +
                                        '.o' + jobid
                                    )
                                try:
                                    shutil.move(file, file[:-2] + '.r')
                                except OSError:
                                    continue
                                myqexec = command_mod.Command(
                                    'myqexec',
                                    args=['-jobid', jobid],
                                    errors='stop'
                                )
                                subtask_mod.Daemon(
                                    myqexec.get_cmdline()).run(file=logfile)
                                return

    def _scheduler_daemon(self):
        Lock(os.path.join(self._myqsdir, 'myqsd.pid')).create()
        while True:
            self._schedule_job()
            time.sleep(2)

    def _start_daemon(self):
        if not os.path.isdir(self._myqsdir):
            try:
                os.makedirs(self._myqsdir)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot created "' +
                    self._myqsdir + '" directory.'
                )
        lock = Lock(os.path.join(self._myqsdir, 'myqsd.pid'))
        if lock.check():
            print('Stopping MyQS batch job scheduler...')
            lock.remove()
        else:
            self._restart()
        print('Starting MyQS batch job scheduler...')
        myqsd = command_mod.CommandFile(
            __file__[:-3],
            args=['-daemon', str(self._slots)]
        )
        subtask_mod.Daemon(myqsd.get_cmdline()).run()

    def run(self):
        """
        Start program
        """
        options = Options()

        self._myqsdir = options.get_myqsdir()
        self._slots = options.get_slots()

        if 'HOME' not in os.environ:
            raise SystemExit(
                sys.argv[0] + ': Cannot determine home directory.')
        if options.get_daemon_flag():
            self._scheduler_daemon()
        else:
            self._start_daemon()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
