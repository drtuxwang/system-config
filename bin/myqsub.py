#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job submission.
"""

import argparse
import glob
import os
import shutil
import signal
import socket
import sys
import time
from typing import List

import task_mod

RELEASE = '2.8.1'


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._release = RELEASE
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_ncpus(self) -> int:
        """
        Return number of CPU slots.
        """
        return self._args.ncpus[0]

    def get_queue(self) -> str:
        """
        Return queue name.
        """
        return self._args.queue[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release +
            ', My Queuing System batch job submission.',
        )

        parser.add_argument(
            '-n',
            nargs=1,
            type=int,
            dest='ncpus',
            default=[1],
            help='Select CPU core slots to reserve for job. Default is 1.'
        )
        parser.add_argument(
            '-q',
            nargs=1,
            dest='queue',
            default=['normal'],
            help='Select "normal" or "express" queue. Default is "normal".'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='batch.sh',
            help='Batch job file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.ncpus[0] < 1:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'the number of cpus.'
            )
        if self._args.queue[0] not in ('normal', 'express'):
            raise SystemExit(
                sys.argv[0] + ': Cannot submit to non-existent queue "' +
                self._args.queue[0] + '".'
            )


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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

    def _lastjob(self) -> int:
        lastjob = os.path.join(self._myqsdir, 'myqs.last')
        if os.path.isfile(lastjob):
            try:
                with open(
                    lastjob,
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
                    try:
                        jobid = int(ifile.readline().strip()) + 1
                    except (OSError, ValueError):
                        jobid = 1
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + lastjob +
                    '" MyQS lastjob file.'
                ) from exception
            if jobid > 32767:
                jobid = 1
        else:
            jobid = 1
        try:
            with open(lastjob, 'w', encoding='utf-8', newline='\n') as ofile:
                print(jobid, file=ofile)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot update "' + lastjob +
                '" MyQS lastjob file.'
            ) from exception
        return jobid

    def _lock(self) -> str:
        while True:
            lockfile = os.path.join(self._myqsdir, 'myqsub.pid')
            if os.path.isfile(lockfile):
                try:
                    with open(
                        lockfile,
                        encoding='utf-8',
                        errors='replace',
                    ) as ifile:
                        try:
                            pid = int(ifile.readline().strip())
                        except (OSError, ValueError):
                            pass
                        else:
                            if not task_mod.Tasks.factory().haspid(pid):
                                os.remove(lockfile)
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' +
                        lockfile + '" MyQS lock file.'
                    ) from exception
            if not os.path.isfile(lockfile):
                try:
                    with open(
                        lockfile,
                        'w',
                        encoding='utf-8',
                        newline='\n',
                    ) as ofile:
                        print(os.getpid(), file=ofile)
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' +
                        lockfile + '" MyQS lock file.'
                    ) from exception
                break
            time.sleep(1)
        return lockfile

    def _myqsd(self) -> None:
        lockfile = os.path.join(self._myqsdir, 'myqsd.pid')
        try:
            with open(lockfile, encoding='utf-8', errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if task_mod.Tasks.factory().haspid(pid):
                        return
                    os.remove(lockfile)
        except OSError:
            pass
        print('MyQS batch job scheduler not running. Run "myqsd" command.')

    def _submit(self, options: Options) -> None:
        tmpfile = os.path.join(self._myqsdir, 'newjob.tmp')
        queue = options.get_queue()
        ncpus = options.get_ncpus()

        for file in options.get_files():
            if not os.path.isfile(file):
                print('MyQS cannot find "' + file + '" batch file.')
                return
            jobid = self._lastjob()
            try:
                with open(
                    tmpfile,
                    'w',
                    encoding='utf-8',
                    newline='\n',
                ) as ofile:
                    print("COMMAND=" + file, file=ofile)
                    print("DIRECTORY=" + os.getcwd(), file=ofile)
                    print("PATH=" + os.environ['PATH'], file=ofile)
                    print("QUEUE=" + queue, file=ofile)
                    print("NCPUS=" + str(ncpus), file=ofile)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + tmpfile +
                    '" temporary file.'
                ) from exception
            shutil.move(
                tmpfile,
                os.path.join(self._myqsdir, str(jobid) + '.q')
            )
            print(
                'Batch job with jobid', jobid, 'has been submitted into MyQS.')
            time.sleep(0.5)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if 'HOME' not in os.environ:
            raise SystemExit(
                sys.argv[0] + ': Cannot determine home directory.')
        self._myqsdir = os.path.join(
            os.environ['HOME'],
            '.config',
            'myqs',
            socket.gethostname().split('.')[0].lower()
        )
        if not os.path.isdir(self._myqsdir):
            try:
                os.makedirs(self._myqsdir)
                os.chmod(self._myqsdir, int('700', 8))
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + self._myqsdir +
                    '" MyQS directory.'
                ) from exception
        lockfile = self._lock()
        self._submit(options)
        os.remove(lockfile)
        self._myqsd()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
