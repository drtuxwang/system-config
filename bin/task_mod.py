#!/usr/bin/env python3
"""
Python task handling utility module

Copyright GPL v2: 2006-2024 By Dr Colin Kong
"""

import functools
import getpass
import os
import re
import signal
import subprocess
import sys
from pathlib import Path
from typing import List

RELEASE = '2.5.2'
VERSION = 20250223


class Tasks:
    """
    This class handles system processess.

    self._process = Dictionary containing process information
    """

    def __init__(self, user: str = None) -> None:
        """
        user = Username or '<all>'
        """
        self._process: dict = {}

        if not user:
            user = _System.get_username()
        self._config(user)

    def _config(self, user: str) -> None:
        raise NotImplementedError

    @staticmethod
    def factory(user: str = None) -> 'Tasks':
        """
        Return Tasks sub class object.
        """
        if _System.is_windows():
            return WindowsTasks(user)
        return PosixTasks(user)

    def pgid2pids(self, pgid: int) -> List[int]:
        """
        Return process ID list with process group ID.

        pgid = Process group ID
        """
        if not isinstance(pgid, int):
            raise InvalidPgidError(
                f'"{__name__}.Tasks" invalid pgid type "{pgid}".',
            )
        pids = []
        for pid in self.get_pids():
            if self._process[pid]['PGID'] == pgid:
                pids.append(pid)
        return sorted(pids)

    def pname2pids(self, pname: str) -> List[int]:
        """
        Return process ID list with program name.

        pname = Program name
        """
        raise NotImplementedError

    def _kill(self, pids: List[int], signame: str) -> None:
        raise NotImplementedError

    def killpids(
        self,
        pids: List[int],
        signame: str = 'KILL',
    ) -> None:
        """
        Kill processes by process ID list.

        pids = List of process IDs
        signame = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        if signame not in ('CONT', 'KILL', 'STOP', 'TERM'):
            raise InvalidSignalError(f'Invalid "{signame}" signal name.')

        if pids:
            self._kill(pids, signame)

    def killpgid(self, pgid: int, signame: str = 'KILL') -> None:
        """
        Kill processes by process group ID.

        pgids = List of process group ID
        signame = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        raise NotImplementedError

    def killpname(self, pname: str, signame: str = 'KILL') -> None:
        """
        Kill all processes with program name.

        pname = Program name
        signame = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        self.killpids(self.pname2pids(pname), signame=signame)

    def haspgid(self, pgid: int) -> bool:
        """
        Return True if process with <pgid> process group ID exists.

        pgid = Process group ID
        """
        if not isinstance(pgid, int):
            raise InvalidPgidError(
                f'"{__name__}.Tasks" invalid pgid type "{pgid}".',
            )
        return self.pgid2pids(pgid) != []

    def haspid(self, pid: int) -> bool:
        """
        Return True if process with <pid> process ID exists.

        pid = Process ID
        """
        if not isinstance(pid, int):
            raise InvalidPidError(
                f'"{__name__}.Tasks" invalid pid type "{pid}".',
            )
        return pid in self._process

    def haspname(self, pname: str) -> bool:
        """
        Return True if process with program name exists.

        pname = Program name
        """
        return self.pname2pids(pname) != []

    def get_ancestor_pids(self, pid: int) -> List[int]:
        """
        Return list of ancestor process IDs.

        pid = Process ID
        """
        apids = []
        if pid in self._process:
            ppid = self._process[pid]['PPID']
            if ppid in self._process:
                apids.extend([ppid] + self.get_ancestor_pids(ppid))
        return apids

    def get_child_pids(self, ppid: int) -> List[int]:
        """
        Return list of child process IDs.

        pid = Parent process ID
        """
        cpids = []
        if ppid in self._process:
            for pid, process in sorted(self._process.items()):
                if process['PPID'] == ppid:
                    cpids.append(pid)
        return cpids

    def get_descendant_pids(self, ppid: int) -> List[int]:
        """
        Return list of descendant process IDs.

        pid = Parent process ID
        """
        dpids = []
        if ppid in self._process:
            for pid, process in sorted(self._process.items()):
                if process['PPID'] == ppid:
                    dpids.extend([pid] + self.get_descendant_pids(pid))
        return dpids

    def get_orphan_pids(self, pgid: int) -> List[int]:
        """
        Return list of orphaned process IDs excluding process group leader.

        pgid = Process group ID
        """
        pids = []
        for pid, process in sorted(self._process.items()):
            if process['PGID'] == pgid:
                if process['PPID'] == 1:
                    if pid != pgid:
                        pids.append(pid)
        return pids

    def get_pids(self) -> List[int]:
        """
        Return list of process IDs.
        """
        return sorted(self._process)

    def get_process(self, pid: int) -> dict:
        """
        Return process dictionary.
        """
        return self._process[pid]


class PosixTasks(Tasks):
    """
    This class handles POSIX system processess.

    self._process = Dictionary containing process information
    """
    signals = {
        'CONT': signal.SIGCONT,
        'KILL': signal.SIGKILL,
        'STOP': signal.SIGSTOP,
        'TERM': signal.SIGTERM,
    }

    def _config(self, user: str) -> None:
        if 'COLUMNS' not in os.environ:
            os.environ['COLUMNS'] = '1024'  # Fix Linux ps width
        command = [
            'ps',
            '-o',
            'ruser pid ppid pgid pri nice tty vsz time etime args'
        ]
        if user == '<all>':
            command.append('-e')
        else:
            command.extend(['-u', user])

        try:
            lines = _System.run_program(command)
        except (CommandNotFoundError, ExecutableCallError) as exception:
            raise SystemExit(exception) from exception

        for line in lines[1:]:
            process: dict = {}
            try:
                process['USER'] = line.split()[0]
                pid = int(line.split()[1])
                process['PPID'] = int(line.split()[2])
                process['PGID'] = int(line.split()[3])
                process['PRI'] = line.split()[4]
                process['NICE'] = line.split()[5]
                process['TTY'] = line.split()[6]
                process['MEMORY'] = int(line.split()[7])
                process['CPUTIME'] = line.split()[8]
                process['ETIME'] = line.split()[9]
                process['COMMAND'] = ' '.join(line.split()[10:])
                self._process[pid] = process
            except (IndexError, ValueError):
                continue

    def pname2pids(self, pname: str) -> List[int]:
        """
        Return process ID list with program name.

        pname = Program name
        """
        isexist = re.compile(f'^(|[^ ]+/){pname}( |$)')

        pids = []
        for pid in self.get_pids():
            if isexist.search(self._process[pid]['COMMAND']):
                pids.append(pid)
        return sorted(pids)

    def _kill(self, pids: List[int], signame: str) -> None:
        for pid in pids:
            try:
                if pid < 0:  # Avoids broken /usr/bin/kill on some Linux
                    os.killpg(-pid, self.signals[signame])
                else:
                    os.kill(pid, self.signals[signame])
            except ProcessLookupError:
                pass

    def killpgid(self, pgid: int, signame: str = 'KILL') -> None:
        """
        Kill processes by process group ID.

        pgids = List of process group ID
        signame = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        self.killpids([-pgid], signame=signame)


class WindowsTasks(Tasks):
    """
    This class handles Windows system processess.

    self._process = Dictionary containing process information
    """

    def _config(self, user: str) -> None:
        try:
            lines = _System.run_program(['tasklist', '/v'])
        except (CommandNotFoundError, ExecutableCallError) as exception:
            raise SystemExit(exception) from exception

        indice = [0]
        position = 0
        for column in lines[2].split():
            position += len(column) + 1
            indice.append(position)
        for line in lines[3:]:
            process: dict = {}
            process['USER'] = line[indice[6]:indice[7]-1].strip()
            if '\\' in process['USER']:
                process['USER'] = process['USER'].split('\\')[1]
            if user in (process['USER'], '<all>'):
                pid = int(line[indice[1]:indice[2]-1])
                process['PPID'] = 1
                process['PGID'] = pid
                process['PRI'] = '?'
                process['NICE'] = '?'
                process['TTY'] = line[indice[2]:indice[3]-1].strip(
                    ).replace('Tcp#', '')
                process['MEMORY'] = int(line[indice[4]:indice[5]-1].strip(
                    ).replace(',', '').replace('.', '').replace(' K', ''))
                process['CPUTIME'] = line[indice[7]:indice[8]-1].strip()
                process['ETIME'] = '?'
                process['COMMAND'] = line[indice[0]:indice[1]-1].strip()
                self._process[pid] = process

    def pname2pids(self, pname: str) -> List[int]:
        """
        Return process ID list with program name.

        pname = Program name
        """
        isexist = re.compile(f'^{pname}([.]exe|$)')

        pids = []
        for pid in self.get_pids():
            if isexist.search(self._process[pid]['COMMAND']):
                pids.append(pid)
        return sorted(pids)

    def _kill(self, pids: List[int], signame: str) -> None:
        command = ['taskkill', '/f']
        for pid in pids:
            command.extend(['/pid', str(pid)])
        try:
            _System.run_program(command)
        except (CommandNotFoundError, ExecutableCallError) as exception:
            raise SystemExit(exception) from exception

    def killpgid(self, pgid: int, signame: str = 'KILL') -> None:
        """
        Kill processes by process group ID.

        pgids = List of process group ID
        signame = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        self.killpids([pgid], signame=signame)


class _System:

    @staticmethod
    def is_windows() -> bool:
        """
        Return True if running on Windows.
        """
        if os.name == 'posix':
            if os.uname()[0].startswith('cygwin'):
                return True
        elif os.name == 'nt':
            return True

        return False

    @staticmethod
    def get_username() -> str:
        """
        Return my username.
        """
        return getpass.getuser()

    @staticmethod
    @functools.lru_cache(maxsize=4)
    def _locate_program(program: str) -> Path:
        for directory in os.environ['PATH'].split(os.pathsep):
            path = Path(directory, program)
            if path.is_file():
                break
        else:
            raise CommandNotFoundError(
                f'Cannot find required "{program}" software.',
            )
        return path

    @classmethod
    def run_program(cls, command: List[str]) -> List[str]:
        """
        Run program in batch mode and return list of lines.
        """
        program = cls._locate_program(command[0])
        lines = []
        try:
            with subprocess.Popen(
                [str(program)] + command[1:],
                shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            ) as child:
                while True:
                    try:
                        bline = child.stdout.readline()
                    except (KeyboardInterrupt, OSError):
                        break
                    if not bline:
                        break
                    line = bline.decode(errors='replace')
                    lines.append(line.rstrip('\n'))
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{program}" program.',
            ) from exception

        return lines


class TaskError(Exception):
    """
    Task module error.
    """


class InvalidPidError(TaskError):
    """
    Task invalid process ID error.
    """


class InvalidPgidError(TaskError):
    """
    Task invalid process group ID error.
    """


class InvalidSignalError(TaskError):
    """
    Task invalid signal error.
    """


class CommandNotFoundError(TaskError):
    """
    Command not found error.
    """


class ExecutableCallError(TaskError):
    """
    Executable call error.
    """


if __name__ == '__main__':
    if sys.argv[-1] in ('-v', '-V', '-version', '--version'):
        print(f"Python task handling utility module {RELEASE} ({VERSION})")
    else:
        help(__name__)
