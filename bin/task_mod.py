#!/usr/bin/env python3
"""
Python task handling utility module

Copyright GPL v2: 2006-2016 By Dr Colin Kong

Version 2.0.0 (2016-02-08)
"""

import os
import re
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Task(object):
    """
    This class handles system processess.

    self._process  = Dictionary containing process information
    """

    def __init__(self, user=None):
        """
        user = Username or '<all>'
        """
        self._process = {}
        self._cache = {}

        if not user:
            user = _System.get_username()
        self._config(user)

    def _config(self, user):
        raise NotImplementedError

    @classmethod
    def factory(cls):
        """
        Return Task sub class object.
        """
        if _System.is_windows():
            return WindowsTask()
        return PosixTask()

    def pgid2pids(self, pgid):
        """
        Return process ID list with process group ID.

        pgid = Process group ID
        """
        if not isinstance(pgid, int):
            raise TaskInvalidPgidError(
                sys.argv[0] + ': "' + __name__ + '.Task" invalid pgid type "' + str(pgid) + '".')
        pids = []
        for pid in self.get_pids():
            if self._process[pid]['PGID'] == pgid:
                pids.append(pid)
        return sorted(pids)

    @staticmethod
    def pname2pids(_):
        """
        Return process ID list with program name.

        pname = Program name
        """
        raise NotImplementedError

    def _kill(self, signal, pids):
        raise NotImplementedError

    def killpids(self, pids, signal='KILL'):
        """
        Kill processes by process ID list.

        pids   = List of process IDs
        signal = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        if signal not in ('CONT', 'KILL', 'STOP', 'TERM'):
            raise TaskInvalidSignalError(sys.argv[0] + ': Invalid "' + signal + '" signal name.')

        if pids:
            self._kill(signal, pids)

    def killpgid(self, pgid, signal='KILL'):
        """
        Kill processes by process group ID.

        pgids = List of process group ID
        signal   = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        raise NotImplementedError

    def killpname(self, pname, signal='KILL'):
        """
        Kill all processes with program name.

        pname  = Program name
        signal = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        self.killpids(self.pname2pids(pname), signal=signal)

    def haspgid(self, pgid):
        """
        Return True if process with <pgid> process group ID exists.

        pgid = Process group ID
        """
        if not isinstance(pgid, int):
            raise TaskInvalidPgidError(
                sys.argv[0] + ': "' + __name__ + '.Task" invalid pgid type "' + str(pgid) + '".')
        return self.pgid2pids(pgid) != []

    def haspid(self, pid):
        """
        Return True if process with <pid> process ID exists.

        pid = Process ID
        """
        if not isinstance(pid, int):
            raise TaskInvalidPidError(
                sys.argv[0] + ': "' + __name__ + '.Task" invalid pid type "' + str(pid) + '".')
        return pid in self._process.keys()

    def haspname(self, pname):
        """
        Return True if process with program name exists.

        pname = Program name
        """
        return self.pname2pids(pname) != []

    def get_ancestor_pids(self, pid):
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

    def get_descendant_pids(self, ppid):
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

    def get_orphan_pids(self, pgid):
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

    def get_pids(self):
        """
        Return list of process IDs.
        """
        return sorted(self._process.keys())

    def get_process(self, pid):
        """
        Return process dictionary.
        """
        return self._process[pid]


class PosixTask(Task):
    """
    This class handles POSIX system processess.

    self._process  = Dictionary containing process information
    """

    def _config(self, user):
        command = syslib.Command(
            'ps', flags=['-o', 'ruser pid ppid pgid pri nice tty vsz time etime args', '-e'])
        if 'COLUMNS' not in os.environ:
            os.environ['COLUMNS'] = '1024'       # Fix Linux ps width
        command.run(mode='batch')

        for line in command.get_output()[1:]:
            process = {}
            process['USER'] = line.split()[0]
            if user in (process['USER'], '<all>'):
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

    def pname2pids(self, pname):
        """
        Return process ID list with program name.

        pname = Program name
        """
        isexist = re.compile('^(|[^ ]+/)' + pname + '( |$)')

        pids = []
        for pid in self.get_pids():
            if isexist.search(self._process[pid]['COMMAND']):
                pids.append(pid)
        return sorted(pids)

    def _kill(self, signal, pids):
        if 'kill' not in self._cache:
            self._cache['kill'] = syslib.Command('kill')

        kill = self._cache['kill']
        kill.set_flags(['-' + signal])
        for pid in pids:
            kill.append_arg(str(pid))
        kill.run(mode='batch')

    def killpgid(self, pgid, signal='KILL'):
        """
        Kill processes by process group ID.

        pgids = List of process group ID
        signal   = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        self.killpids([-pgid], signal=signal)


class WindowsTask(Task):
    """
    This class handles Windows system processess.

    self._process = Dictionary containing process information
    """

    def _config(self, user):
        command = syslib.Command('tasklist', flags=['/v'])
        command.run(mode='batch')

        indice = [0]
        position = 0
        for column in command.get_output()[2].split():
            position += len(column) + 1
            indice.append(position)
        for line in command.get_output()[3:]:
            process = {}
            process['USER'] = line[indice[6]:indice[7]-1].strip()
            if '\\' in process['USER']:
                process['USER'] = process['USER'].split('\\')[1]
            if user in (process['USER'], '<all>'):
                pid = int(line[indice[1]:indice[2]-1])
                process['PPID'] = 1
                process['PGID'] = pid
                process['PRI'] = '?'
                process['NICE'] = '?'
                process['TTY'] = line[indice[2]:indice[3]-1].strip().replace('Tcp#', '')
                process['MEMORY'] = int(line[indice[4]:indice[5]-1].strip().replace(
                    ',', '').replace('.', '').replace(' K', ''))
                process['CPUTIME'] = line[indice[7]:indice[8]-1].strip()
                process['ETIME'] = '?'
                process['COMMAND'] = line[indice[0]:indice[1]-1].strip()
                self._process[pid] = process

    def pname2pids(self, pname):
        """
        Return process ID list with program name.

        pname = Program name
        """
        isexist = re.compile('^' + pname + '([.]exe|$)')

        pids = []
        for pid in self.get_pids():
            if isexist.search(self._process[pid]['COMMAND']):
                pids.append(pid)
        return sorted(pids)

    def _kill(self, signal, pids):
        if 'kill' not in self._cache:
            self._cache['kill'] = syslib.Command('taskkill', flags=['/f'])

        kill = self._cache['kill']
        for pid in pids:
            kill.extend_args(['/pid', str(pid)])
        kill.run(mode='batch')

    def killpgid(self, pgid, signal='KILL'):
        """
        Kill processes by process group ID.

        pgids = List of process group ID
        signal   = Signal name to send ('CONT', 'KILL', 'STOP', 'TERM')
        """
        self.killpids([pgid], signal=signal)


class _System(object):

    @classmethod
    def is_windows(cls):
        """
        Return True if running on Windows.
        """
        if os.name == 'posix':
            if os.uname()[0].startswith('cygwin'):
                return True
        elif os.name == 'nt':
            return True

        return False

    @classmethod
    def get_username(cls):
        """
        Return my username.
        """
        for environment in ('LOGNAME', 'USER', 'USERNAME'):
            if environment in os.environ:
                return os.environ[environment]
        return 'Unknown'


class TaskModError(SystemExit):
    """
    Task module error.

    self.args = Arguments
    """

    def __init__(self, message):
        """
        message = Error message
        """
        super().__init__()
        self.args = (message,)

    def get_args(self):
        """
        Return arguments
        """
        return self.args


class TaskInvalidPidError(TaskModError):
    """
    Task invalid process ID error.
    """


class TaskInvalidPgidError(TaskModError):
    """
    Task invalid process group ID error.
    """


class TaskInvalidSignalError(TaskModError):
    """
    Task invalid signal error.
    """


if __name__ == '__main__':
    help(__name__)
