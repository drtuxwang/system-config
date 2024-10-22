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
from typing import Generator, List

from command_mod import Command, CommandFile
from logging_mod import Message
from subtask_mod import Task
from task_mod import Tasks

RELEASE = '3.2.0'
VERSION = 20241021


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_add_flag(self) -> str:
        """
        Return add job flag.
        """
        return self._args.add_flag

    def get_multi_flag(self) -> str:
        """
        Return multi job flag.
        """
        return self._args.multi_flag

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

    def get_cmdline(self) -> List[str]:
        """
        Return command line.
        """
        return self._args.cmdline

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description=f"MyQS v{RELEASE}, "
            "My Queuing System batch job submission.",
        )

        parser.add_argument(
            '-v',
            '-V',
            '-version',
            '--version',
            action='version',
            version=f"MyQS {RELEASE} ({VERSION})",
        )
        parser.add_argument(
            '-a',
            dest='add_flag',
            action='store_true',
            help="Add batch jobs for new command only.",
        )
        parser.add_argument(
            '-m',
            dest='multi_flag',
            action='store_true',
            help="Submit multiple batch jobs.",
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
            choices=('normal', 'express'),
            default=['normal'],
            help='Select "normal" or "express" queue. Default is "normal".',
        )
        parser.add_argument(
            'cmdline',
            nargs='+',
            metavar='command',
            help='Batch job command (use "--" to protect flags)',
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
            if jobid > 99999:
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
                            if not Tasks.factory().haspid(pid):
                                path.unlink()
                except OSError as exception:
                    raise SystemExit(
                        f"{sys.argv[0]}: MyQS cannot obtain lock: {path}"
                    ) from exception
            if not path.is_file():
                try:
                    with path.open('w') as ofile:
                        print(os.getpid(), file=ofile)
                except OSError as exception:
                    raise SystemExit(
                        f"{sys.argv[0]}: MyQS cannot create lock: {path}"
                    ) from exception
                break
            time.sleep(1)
        return path

    def _has_myqsd(self) -> bool:
        path = Path(self._myqsdir, 'myqsd.pid')
        try:
            with path.open(errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if Tasks.factory().haspid(pid):
                        return True
                    path.unlink()
        except OSError:
            pass
        return False

    def _new_jobs(
        self,
        cmdlines: List[List[str]],
    ) -> Generator[List[str], None, None]:
        commands = set()
        for _ in range(2):  # Check existig jobs twice
            for path in [Path(x) for x in self._myqsdir.glob('*.[dfqr]')]:
                try:
                    with path.open() as ifile:
                        for line in ifile:
                            if line.startswith('COMMAND='):
                                commands.add(line.rstrip().split('=', 1)[-1])
                                break
                except OSError:
                    pass

        for cmdline in cmdlines:
            command = Command.args2cmd(cmdline)
            if command not in commands:
                commands.add(command)
                yield cmdline

    def _submit(self, options: Options) -> None:
        path_new = Path(self._myqsdir, 'newjob.tmp')
        queue = options.get_queue()
        ncpus = options.get_ncpus()

        if options.get_multi_flag():
            cmdlines = [[x] for x in options.get_cmdline()]
        else:
            cmdlines = [options.get_cmdline()]
        if options.get_add_flag():
            cmdlines = list(self._new_jobs(cmdlines))

        for cmdline in cmdlines:
            command: Command
            if Path(cmdline[0]).is_file():
                command = CommandFile(cmdline[0])
            else:
                command = Command(cmdline[0], errors='ignore')
                if not command.is_found():
                    print(f'MyQS cannot find "{cmdline[0]}" command.')
                    return
            if not os.access(command.get_file(), os.X_OK):
                print(f'MyQS cannot execute "{command.get_file()}" command.')
                return

            jobid = self._lastjob()
            job_command = command.args2cmd(cmdline)
            if Message(job_command).width() <= 45:
                job_name = job_command
            elif len(cmdline) == 2 and not os.access(cmdline[1], os.X_OK):
                job_name = Path(cmdline[1]).name
            else:
                job_name = Message(job_command).get(45)
            try:
                with path_new.open('w') as ofile:
                    print(f"JOBID={jobid}", file=ofile)
                    print(f"JOBNAME={job_name}", file=ofile)
                    print(f"QUEUE={queue}", file=ofile)
                    print(f"NCPUS={ncpus}", file=ofile)
                    print(f"DIRECTORY={os.getcwd()}", file=ofile)
                    print(f"COMMAND={job_command}", file=ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{path_new}" '
                    'temporary file.'
                ) from exception
            path_new.replace(Path(self._myqsdir, f'{jobid}.q'))
            print(f'MyQS jobid {jobid} submitted: {command.args2cmd(cmdline)}')

            time.sleep(0.25)

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

        if not self._has_myqsd():
            myqsd = Command('myqsd', args=['1'], errors='stop')
            Task(myqsd.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
