#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job submission.
"""

import argparse
import os
import signal
import socket
import sys
import time
from pathlib import Path
from typing import List

import task_mod

RELEASE = '2.8.6'


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
            description=f"MyQS v{self._release}, My Queuing System "
            f"batch job submission.",
        )

        parser.add_argument(
            '-n',
            nargs=1,
            type=int,
            dest='ncpus',
            default=[1],
            help="Select CPU core slots to reserve for job. Default is 1.",
        )
        parser.add_argument(
            '-q',
            nargs=1,
            dest='queue',
            default=['normal'],
            help='Select "normal" or "express" queue. Default is "normal".',
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='batch.sh',
            help="Batch job file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.ncpus[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a positive integer for '
                'the number of cpus.'
            )
        if self._args.queue[0] not in ('normal', 'express'):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot submit to non-existent queue '
                f'"{self._args.queue[0]}".',
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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    def _lastjob(self) -> int:
        path = Path(self._myqsdir, 'myqs.last')
        if path.is_file():
            try:
                with path.open(errors='replace') as ifile:
                    try:
                        jobid = int(ifile.readline().strip()) + 1
                    except (OSError, ValueError):
                        jobid = 1
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read '
                    f'"{path}" MyQS lastjob file.',
                ) from exception
            if jobid > 32767:
                jobid = 1
        else:
            jobid = 1
        try:
            with path.open('w') as ofile:
                print(jobid, file=ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot update '
                f'"{path}" MyQS lastjob file.',
            ) from exception
        return jobid

    def _lock(self) -> Path:
        while True:
            path = Path(self._myqsdir, 'myqsub.pid')
            if path.is_file():
                try:
                    with path.open(errors='replace') as ifile:
                        try:
                            pid = int(ifile.readline().strip())
                        except (OSError, ValueError):
                            pass
                        else:
                            if not task_mod.Tasks.factory().haspid(pid):
                                path.unlink()
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot read '
                        f'"{path}" MyQS lock file.',
                    ) from exception
            if not path.is_file():
                try:
                    with path.open('w') as ofile:
                        print(os.getpid(), file=ofile)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create '
                        f'"{path}" MyQS lock file.'
                    ) from exception
                break
            time.sleep(1)
        return path

    def _myqsd(self) -> None:
        path = Path(self._myqsdir, 'myqsd.pid')
        try:
            with path.open(errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if task_mod.Tasks.factory().haspid(pid):
                        return
                    path.unlink()
        except OSError:
            pass
        print('MyQS batch job scheduler not running. Run "myqsd" command.')

    def _submit(self, options: Options) -> None:
        path_new = Path(self._myqsdir, 'newjob.tmp')
        queue = options.get_queue()
        ncpus = options.get_ncpus()

        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                print(f'MyQS cannot find "{path}" batch file.')
                return
            jobid = self._lastjob()
            try:
                with path_new.open('w') as ofile:
                    print(f"COMMAND={path}", file=ofile)
                    print(f"DIRECTORY={os.getcwd()}", file=ofile)
                    print(f"PATH={os.environ['PATH']}", file=ofile)
                    print(f"QUEUE={queue}", file=ofile)
                    print(f"NCPUS={ncpus}", file=ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{path_new}" '
                    'temporary file.'
                ) from exception
            path_new.replace(Path(self._myqsdir, f'{jobid}.q'))
            print(
                f'Batch job with jobid {jobid} has been submitted into MyQS.',
            )

            time.sleep(0.5)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine home directory.",
            )
        self._myqsdir = Path(
            Path.home(),
            '.config',
            'myqs',
            socket.gethostname().split('.')[0].lower()
        )
        if not self._myqsdir.is_dir():
            try:
                os.makedirs(self._myqsdir)
                os.chmod(self._myqsdir, 0o700)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create '
                    f'"{self._myqsdir}" MyQS directory.',
                ) from exception
        lock_path = self._lock()
        self._submit(options)
        lock_path.unlink()
        self._myqsd()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
