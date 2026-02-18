#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job scheduler daemon
"""

import argparse
import os
import signal
import socket
import sys
import time
from pathlib import Path
from typing import List

from command_mod import Command, CommandFile
from subtask_mod import Daemon
from task_mod import Tasks

RELEASE = '3.3.2'
VERSION = 20260215
PURGE_TIME = 604800


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_daemon_flag(self) -> bool:
        """
        Return daemon flag.
        """
        return self._args.daemon_flag

    def get_myqsdir(self) -> Path:
        """
        Return myqs directory.
        """
        return self._myqsdir

    def get_slots(self) -> int:
        """
        Return CPU core slots.
        """
        return self._args.slots[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description=f"MyQS v{RELEASE}, "
            "My Queuing System batch scheduler daemon.",
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
            '-daemon',
            dest='daemon_flag',
            action='store_true',
            help="Start batch job daemon.",
        )
        parser.add_argument(
            'slots',
            nargs=1,
            type=int,
            help="Number of CPU execution slots to create "
            "(0 = express only, -1 = disabled).",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._myqsdir = Path(
            Path.home(),
            '.config',
            'myqs',
            socket.gethostname().split('.')[0].lower()
        )

        slots = self._args.slots[0]
        if slots < 0 or slots > os.cpu_count():
            raise SystemExit(
                f"{sys.argv[0]}: Invalid number of CPU execution slots "
                f"(0-{os.cpu_count()})"
            )


class Lock:
    """
    Lock class
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._pid = -1
        try:
            with path.open(errors='replace') as ifile:
                try:
                    self._pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
        except OSError:
            pass

    def check(self) -> int:
        """
        Return True if lock exists
        """
        return Tasks.factory().haspid(self._pid)

    def create(self) -> None:
        """
        Create lock file
        """
        try:
            with self._path.open('w') as ofile:
                print(os.getpid(), file=ofile)
        except OSError as exception:
            raise SystemExit(
                f"{sys.argv[0]}: MyQS cannot create lock: {self._path}"
            ) from exception
        time.sleep(1)
        try:
            with self._path.open(errors='replace') as ifile:
                try:
                    int(ifile.readline().strip())
                except (OSError, ValueError) as exception:
                    raise SystemExit(0) from exception
                if not Tasks.factory().haspid(os.getpid()):
                    raise SystemExit(
                        f"{sys.argv[0]}: MyQS cannot obtain lock: {self._path}"
                    )
        except OSError:
            pass

    def remove(self) -> None:
        """
        Remove lock file
        """
        Tasks.factory().killpids([self._pid])
        try:
            self._path.unlink()
        except OSError as exception:
            raise SystemExit(
                f"{sys.argv[0]}: MyQS cannot remove lock: {self._path}"
            ) from exception


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

    def _requeue(self) -> None:
        for path in sorted(self._myqsdir.glob('*.r'), key=lambda s: s.stem):
            try:
                with path.open(errors='replace') as ifile:
                    info = {}
                    for line in ifile:
                        line = line.strip()
                        if '=' in line:
                            info[line.split('=')[0]] = line.split('=', 1)[1]
            except OSError:
                continue
            try:
                pgid = int(info.get('PGID', ''))
            except ValueError:
                continue
            if not Tasks.factory().haspgid(pgid):
                jobid = path.stem
                print(f'MyQS jobid "{jobid}" re-queued after system restart.')
                path.replace(path.with_suffix('.q'))

    def _purge_job(self, delay: int) -> None:
        for path in self._myqsdir.glob('*.[df]'):
            if time.time() - path.stat().st_mtime > delay:
                print(f"MyQS purging finished job: {path}")
                path.unlink()

    @staticmethod
    def _get_info(path: Path) -> dict:
        info = {}
        try:
            with path.open(errors='replace') as ifile:
                for line in ifile:
                    line = line.strip()
                    if '=' in line:
                        key, value = line.split('=', 1)
                        info[key] = value
        except OSError:
            return {}
        return info

    def _schedule_job(self) -> None:
        slots_used = 0
        express_queued = False
        for path in [Path(x) for x in self._myqsdir.glob('*.r')]:
            info = self._get_info(path)
            if 'PGID' in info:
                if not Tasks.factory().haspgid(int(info['PGID'])):
                    time.sleep(0.25)
                    try:
                        path.unlink()
                    except OSError:
                        continue
            slots_used += int(info.get('NCPUS', '0'))

        free_slots = self._slots - slots_used
        if not slots_used:
            free_slots = os.cpu_count()
        self._attempt('express', free_slots)
        self._attempt('normal', free_slots)

    def _attempt(self, queue: str, free_slots: int) -> bool:
        for path in sorted(
            self._myqsdir.glob('*.q'),
            key=lambda s: int(s.stem),
        ):
            info = self._get_info(path)
            if info.get('QUEUE', '') == queue and info.get('NCPUS'):
                if free_slots >= int(info['NCPUS']):
                    jobid = path.stem
                    myqexec = Command('myqexec', errors='stop')
                    myqexec.set_args(['-jobid', jobid])
                    log_file = f"{Path(info.get('JOBNAME')).stem}.o{jobid}"
                    if os.access(info['DIRECTORY'], os.W_OK):
                        log_path = Path(info['DIRECTORY'], log_file)
                    else:
                        log_path = Path(Path.home(), log_file)
                    try:
                        with path.open('a') as ofile:
                            print(f"LOGFILE={log_path}", file=ofile)
                        path.replace(path.with_suffix('.r'))
                    except OSError:
                        continue
                    print(f'MyQS job starting: {log_path}')
                    Daemon(myqexec.get_cmdline()).run(file=str(log_path))
                    return True
        return False

    def _scheduler_daemon(self) -> None:
        self._requeue()
        Lock(Path(self._myqsdir, 'myqsd.pid')).create()
        while True:
            self._purge_job(PURGE_TIME)  # Every 5min
            for _ in range(150):
                self._schedule_job()
                time.sleep(2)

    def _start_daemon(self) -> None:
        if not self._myqsdir.is_dir():
            try:
                os.makedirs(self._myqsdir)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot created '
                    f'"{self._myqsdir}" directory.',
                ) from exception

        lock = Lock(Path(self._myqsdir, 'myqsd.pid'))
        if lock.check():
            print("Stopping MyQS batch job scheduler...")
            lock.remove()
        print("Starting MyQS batch job scheduler...")
        myqsd = CommandFile(__file__[:-3], args=['-daemon', self._slots])
        Daemon(myqsd.get_cmdline()).run()

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._myqsdir = options.get_myqsdir()
        self._slots = options.get_slots()

        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine home directory.",
            )
        if options.get_daemon_flag():
            self._scheduler_daemon()
        else:
            self._start_daemon()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
