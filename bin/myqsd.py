#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job scheduler daemon
"""

import argparse
import glob
import os
import signal
import socket
import sys
import time
from pathlib import Path
from typing import List

import command_mod
import subtask_mod
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
            description=f"MyQS v{self._release}, My Queuing System "
            f"batch scheduler daemon.",
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
            help="The maximum number of CPU execution slots to create.",
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

        if self._args.slots[0] < 1:
            raise SystemExit(
                f"{sys.argv[0]}: You must specific a positive integer "
                "for the number of slots.",
            )


class Lock:
    """
    Lock class
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._pid = -1
        try:
            with path.open(encoding='utf-8', errors='replace') as ifile:
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
        return task_mod.Tasks.factory().haspid(self._pid)

    def create(self) -> None:
        """
        Create lock file
        """
        try:
            with self._path.open(
                'w',
                encoding='utf-8',
                newline='\n',
            ) as ofile:
                print(os.getpid(), file=ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot create '
                f'"{self._path}" MyQS scheduler lock file.',
            ) from exception
        time.sleep(1)
        try:
            with self._path.open(encoding='utf-8', errors='replace') as ifile:
                try:
                    int(ifile.readline().strip())
                except (OSError, ValueError) as exception:
                    raise SystemExit(0) from exception
                else:
                    if not task_mod.Tasks.factory().haspid(os.getpid()):
                        raise SystemExit(
                            f"{sys.argv[0]}: "
                            "Cannot obtain MyQS scheduler lock file.",
                        )
        except OSError:
            return

    def remove(self) -> None:
        """
        Remove lock file
        """
        task_mod.Tasks.factory().killpids([self._pid])
        try:
            self._path.unlink()
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot remove "{self._path}" lock file.',
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _restart(self) -> None:
        for path in sorted(self._myqsdir.glob('*.r'), key=lambda s: s.stem):
            try:
                with path.open(
                    encoding='utf-8',
                    errors='replace',
                ) as ifile:
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
                    jobid = path.stem
                    print(
                        'Batch job with jobid '
                        f'"{jobid}" being requeued after system restart...',
                    )
                    path.replace(f'{path.stem}.q')

    def _schedule_job(self) -> None:
        running = 0
        for file in self._myqsdir.glob('*.r'):
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
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

    def _attempt(self, free_slots: int) -> None:
        for queue in ('express', 'normal'):
            for path in sorted(
                self._myqsdir.glob('*.q'),
                key=lambda s: int(s.stem),
            ):
                try:
                    with path.open(
                        encoding='utf-8',
                        errors='replace',
                    ) as ifile:
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
                                jobid = path.stem
                                if Path(info['DIRECTORY']).is_dir():
                                    log_path = Path(
                                        info['DIRECTORY'],
                                        f"{Path(info['COMMAND']).name}"
                                        f".o{jobid}",
                                    )
                                else:
                                    log_path = Path(
                                        str(Path.home()),
                                        f"{Path(info['COMMAND']).name}"
                                        f".o{jobid}",
                                    )
                                try:
                                    path.replace(f'{path.stem}.r')
                                except OSError:
                                    continue
                                myqexec = command_mod.Command(
                                    'myqexec',
                                    args=['-jobid', jobid],
                                    errors='stop'
                                )
                                subtask_mod.Daemon(
                                    myqexec.get_cmdline()).run(
                                        file=str(log_path)
                                    )
                                return

    def _scheduler_daemon(self) -> None:
        Lock(Path(self._myqsdir, 'myqsd.pid')).create()
        while True:
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
        else:
            self._restart()
        print("Starting MyQS batch job scheduler...")
        myqsd = command_mod.CommandFile(
            __file__[:-3],
            args=['-daemon', str(self._slots)]
        )
        subtask_mod.Daemon(myqsd.get_cmdline()).run()

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
