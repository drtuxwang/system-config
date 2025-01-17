#!/usr/bin/env python3
"""
Python sub task handling module

Copyright GPL v2: 2006-2024 By Dr Colin Kong
"""

import copy
import os
import re
import signal
import subprocess
import sys
import types
from pathlib import Path
from typing import Any, Callable, Dict, List, Union


RELEASE = '2.4.1'
VERSION = 20241026

BUFFER_SIZE = 131072


class Task:
    """
    This class handles running sub process interactively.
    """

    def __init__(self, cmdline: list) -> None:
        """
        cmdline = Command line as a list
        """
        self._file = str(cmdline[0])
        self._cmdline = [str(x) for x in cmdline]
        if os.name == 'nt':
            if '|' in cmdline:
                raise PipeNotSupportedError('Windows does not support pipes.')
            try:
                with Path(cmdline[0]).open(errors='replace') as ifile:
                    if ifile.readline().startswith('#!/usr/bin/env python'):
                        self._cmdline = [sys.executable, '-B'] + cmdline
            except OSError:
                pass
        self._status: dict = {'output': [], 'error': [], 'exitcode': 0}

    def get_cmdline(self) -> List[str]:
        """
        Return the command line as a list.
        """
        return self._cmdline

    def get_file(self) -> str:
        """
        Return file location
        """
        return self._file

    def has_output(self) -> bool:
        """
        Return True if stdout used.
        """
        return self._status['output']

    def is_match_output(self, pattern: str) -> bool:
        """
        Return True if stdout has pattern.

        pattern = Regular expression
        """
        ispattern = re.compile(pattern)
        for line in self._status['output']:
            if ispattern.search(line):
                return True
        return False

    def get_output(self, pattern: str = '') -> List[str]:
        """
        Return list of lines in stdout that match pattern.
        If no pattern return all.

        pattern = Regular expression
        """
        if pattern:
            output = []
            ismatch = re.compile(pattern)
            for line in self._status['output']:
                if ismatch.search(line):
                    output.append(line)
        else:
            output = self._status['output']
        return output

    def has_error(self) -> bool:
        """
        Return True if stderr used.
        """
        return self._status['error']

    def is_match_error(self, pattern: str) -> bool:
        """
        Return True if stderr has pattern.

        pattern = Regular expression
        """
        ispattern = re.compile(pattern)
        for line in self._status['error']:
            if ispattern.search(line):
                return True
        return False

    def get_error(self, pattern: str = '') -> List[str]:
        """
        Return list of lines in stderr that match pattern.
        If no pattern return all.

        pattern = Regular expression
        """
        if pattern:
            error = []
            ismatch = re.compile(pattern)
            for line in self._status['error']:
                if ismatch.search(line):
                    error.append(line)
        else:
            error = self._status['error']
        return error

    def get_exitcode(self) -> int:
        """
        Return exitcode of run.
        """
        return self._status['exitcode']

    @staticmethod
    def _parse_keys(keys: Any, **kwargs: Any) -> dict:
        if set(kwargs.keys()) - set(keys):
            raise TaskKeywordError(
                'Unsupported keyword '
                f'"{list(set(kwargs.keys()) - set(keys))[0]}".',
            )
        info: dict = {}
        for key in keys:
            try:
                info[key] = kwargs[key]
            except KeyError:
                info[key] = '' if key in ('file', 'pattern') else None
        try:
            env: Dict[Any, Any] = copy.copy(kwargs['env'])
            for key in os.environ:
                if key not in env:
                    env[key] = os.environ[key]
                elif env[key] is None:
                    del env[key]
            for key in env:
                if env[key] is None:
                    del env[key]
            info['env'] = env
        except KeyError:
            info['env'] = None
        return info

    @staticmethod
    def _send_stdin(child: subprocess.Popen, info: dict) -> None:

        for line in info['stdin']:
            try:
                child.stdin.write(line.encode() + b"\n")
            except OSError:
                break
        child.stdin.close()

    @staticmethod
    def _recv_stdout(child: subprocess.Popen, info: dict) -> None:
        ismatch = re.compile(info['pattern']) if info['pattern'] else None
        replace = info['replace']

        while True:
            try:
                line = child.stdout.readline().decode(errors='replace')
            except (KeyboardInterrupt, OSError):
                break
            if not line:
                break
            if not ismatch or not ismatch.search(line):
                sys.stdout.write(line.replace(replace[0], replace[1]))

    @staticmethod
    def _recv_stderr(child: subprocess.Popen, info: dict) -> None:
        ismatch = re.compile(info['pattern']) if info['pattern'] else None
        replace = info['replace']

        while True:
            try:
                line = child.stderr.readline().decode(errors='replace')
            except (KeyboardInterrupt, OSError):
                break
            if not line:
                break
            if not ismatch or not ismatch.search(line):
                sys.stderr.write(line.replace(replace[0], replace[1]))

    @staticmethod
    def _interactive_run(cmdline: List[str], info: dict) -> int:
        command: Union[List[str], str] = cmdline

        if '|' in cmdline:
            pipe = True
            command = subprocess.list2cmdline(cmdline)
        else:
            pipe = False

        try:
            return subprocess.call(command, env=info['env'], shell=pipe)
        except KeyboardInterrupt:
            return 130

    @staticmethod
    def _start_child(cmdline: List[str], info: dict) -> subprocess.Popen:
        command: Union[List[str], str] = cmdline

        if '|' in cmdline:
            pipe = True
            command = subprocess.list2cmdline(cmdline)
        else:
            pipe = False

        stderr = subprocess.STDOUT if info['error2output'] else subprocess.PIPE
        return subprocess.Popen(  # pylint: disable=consider-using-with
            command,
            env=info['env'],
            shell=pipe,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=stderr
        )

    def _interactive_child_run(self, cmdline: List[str], info: dict) -> int:
        child: subprocess.Popen = self._start_child(cmdline, info)
        if not info['replace']:
            info['replace'] = ('', '')

        if info['stdin']:
            self._send_stdin(child, info)
        try:
            self._recv_stdout(child, info)
        except OSError as exception:
            raise OutputWriteError(
                f'Error writing stderr of "{self._file}" program.',
            ) from exception
        if not info['error2output']:
            try:
                self._recv_stderr(child, info)
            except OSError as exception:
                raise OutputWriteError(
                    f'Error  writing output of "{self._file}" program.',
                ) from exception
        return child.wait()

    def run(self, **kwargs: Any) -> Any:
        """
        Run process interactively and return exits status.

        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        error2output = Flag to send stderr to stdout
        pattern = Regular expression for removing output
        replace = Replace all occurance (str1, str2)
        stdin = List of str for stdin input
        """
        info = self._parse_keys((
            'directory',
            'env',
            'error2output',
            'pattern',
            'replace',
            'stdin',
        ), **kwargs)

        if not sys.stdout.isatty():
            sys.stdout.flush()
        if not sys.stderr.isatty():
            sys.stderr.flush()
        if info['directory']:
            pwd = Path.cwd()
            os.chdir(info['directory'])
        try:
            if (
                info['error2output'] or
                info['pattern'] or
                info['replace'] or
                info['stdin']
            ):
                self._status['exitcode'] = self._interactive_child_run(
                    self._cmdline, info
                )
            else:
                self._status['exitcode'] = self._interactive_run(
                    self._cmdline,
                    info,
                )
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{self._file}" program.',
            ) from exception
        if info['directory']:
            os.chdir(pwd)
        return self._status['exitcode']


class Background(Task):
    """
    This class handles running sub process in background mode.
    """

    @staticmethod
    def _start_background_run(cmdline: List[str], info: dict) -> None:
        command: Union[List[str], str] = cmdline

        if '|' in cmdline:
            pipe = True
            command = subprocess.list2cmdline(cmdline)
        else:
            pipe = False

        if info['pattern']:
            os.environ['_SUBTASK_MOD_BACKGROUND_FILTER'] = info['pattern']
            subprocess.Popen(  # pylint: disable=consider-using-with
                [sys.executable, '-B', __file__] + cmdline,
                shell=pipe,
                env=info['env']
            )
            del os.environ['_SUBTASK_MOD_BACKGROUND_FILTER']
        else:
            subprocess.Popen(  # pylint: disable=consider-using-with
                command,
                shell=pipe,
                env=info['env'],
            )

    def run(self, **kwargs: Any) -> None:
        """
        Start background process.

        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        error2output = Flag to send stderr to stdout
        pattern = Regular expression for removing output
        """
        info = self._parse_keys(
            ('directory', 'env', 'error2output', 'pattern', 'stdin'),
            **kwargs
        )

        if not sys.stdout.isatty():
            sys.stdout.flush()
        if not sys.stderr.isatty():
            sys.stderr.flush()
        if info['directory']:
            pwd = os.getcwd()
            os.chdir(info['directory'])
        try:
            self._start_background_run(self._cmdline, info)
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{self._file}" program.',
            ) from exception
        if info['directory']:
            os.chdir(pwd)


class Batch(Task):
    """
    This class handles running sub process in batch mode.
    """

    @staticmethod
    def _write_file(child: subprocess.Popen, path: Path, append: bool) -> None:
        mode = 'ab' if append else 'wb'
        try:
            with path.open(mode) as ofile:
                while True:
                    chunk = child.stdout.read(4096)
                    if not chunk:
                        break
                    ofile.write(chunk)
        except KeyboardInterrupt:
            pass
        except OSError as exception:
            if append:
                raise OutputWriteError(
                    f'Cannot append to "{path}" output file.',
                ) from exception
            raise OutputWriteError(
                f'Cannot create "{path}" output file.',
            ) from exception

    def _batch_run(self, cmdline: List[str], info: dict) -> int:
        child = self._start_child(cmdline, info)
        if info['stdin']:
            self._send_stdin(child, info)

        ismatch = re.compile(info['pattern'])
        file = info['file']
        if file:
            self._write_file(child, Path(file), info['append'])
        else:
            while True:
                try:
                    line = child.stdout.readline().decode(errors='replace')
                except (KeyboardInterrupt, OSError):
                    break
                if not line:
                    break
                if ismatch.search(line):
                    self._status['output'].append(line.rstrip('\n'))
        if not info['error2output']:
            while True:
                try:
                    line = child.stderr.readline().decode(errors='replace')
                except (KeyboardInterrupt, OSError):
                    break
                if not line:
                    break
                if ismatch.search(line):
                    self._status['error'].append(line.rstrip('\n'))
        return child.wait()

    def run(self, **kwargs: Any) -> int:
        """
        Run process in batch mode and return exit status.

        append = Flag to append to output_file
        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        error2output = Flag to send stderr to stdout
        file = Redirect stdout to file
        pattern = Regular expression for selecting output
        stdin = List of str for stdin input
        """
        self._status['output'] = []
        self._status['error'] = []
        info = self._parse_keys((
            'append',
            'directory',
            'env',
            'error2output',
            'file',
            'pattern',
            'stdin',
        ), **kwargs)

        if info['directory']:
            pwd = os.getcwd()
            os.chdir(info['directory'])
        try:
            self._status['exitcode'] = self._batch_run(self._cmdline, info)
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{self._file}" program.',
            ) from exception
        if info['directory']:
            os.chdir(pwd)

        return self._status['exitcode']


class Child(Task):
    """
    This class handles running sub process as a child process.
    """

    def run(self, **kwargs: Any) -> subprocess.Popen:
        """
        Return child process object with stdin, stdout and stderr pipes.

        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        error2output = Flag to send stderr to stdout
        """
        info = self._parse_keys(('directory', 'env', 'error2output'), **kwargs)

        if info['directory']:
            pwd = Path.cwd()
            os.chdir(info['directory'])
        try:
            return self._start_child(self._cmdline, info)
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{self._file}" program.',
            ) from exception
        if info['directory']:
            os.chdir(pwd)


class Daemon(Task):
    """
    This class handles running sub process as a daemon.
    """

    @staticmethod
    def _start_daemon(cmdline: List[str], info: dict) -> None:
        os.environ['_SUBTASK_MOD_DAEMON_FILE'] = str(info['file'])

        if '|' in cmdline:
            subprocess.Popen(  # pylint: disable=consider-using-with
                subprocess.list2cmdline(
                    [sys.executable, '-B', __file__] + cmdline
                ),
                shell=True,
                env=info['env'],
            )
        else:
            subprocess.Popen(  # pylint: disable=consider-using-with
                [sys.executable, '-B', __file__] + cmdline,
                env=info['env'],
            )

        del os.environ['_SUBTASK_MOD_DAEMON_FILE']

    def run(self, **kwargs: Any) -> None:
        """
        Replace current process with new executable.

        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        file =  Log stdout & stderr to file
        """
        info = self._parse_keys(('directory', 'env', 'file'), **kwargs)

        if info['directory']:
            pwd = Path.cwd()
            os.chdir(info['directory'])
        try:
            self._start_daemon(self._cmdline, info)
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{self._file}" program.',
            ) from exception
        if info['directory']:
            os.chdir(pwd)


class Exec(Task):
    """
    This class handles replaces current process with new executable.
    """

    @staticmethod
    def _windows_exec_run(cmdline: List[str], info: dict) -> None:
        stdout_write = sys.stdout.buffer.write
        stderr_write = sys.stderr.buffer.write
        try:
            with subprocess.Popen(
                cmdline,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=info['env']
            ) as child:
                while True:
                    byte = child.stdout.read(1)
                    if not byte:
                        break
                    stdout_write(byte)
                    sys.stdout.flush()
                while True:
                    byte = child.stderr.read(1)
                    if not byte:
                        break
                    stderr_write(byte)
                    sys.stderr.flush()
                exitcode = child.wait()
        except OSError:
            exitcode = 1
        raise SystemExit(exitcode)

    @classmethod
    def _exec_run(cls, cmdline: List[str], info: dict) -> None:
        if '|' in cmdline:
            raise PipeNotSupportedError('Exec does not support pipe.')

        if os.name == 'nt':  # Avoids Windows execvpn exit status bug
            cls._windows_exec_run(cmdline, info)
        else:
            os.execvpe(cmdline[0], cmdline, env=info['env'])

    def run(self, **kwargs: Any) -> None:
        """
        Replace current process with new executable.

        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        """
        info = self._parse_keys(('directory', 'env'), **kwargs)

        if info['directory']:
            os.chdir(info['directory'])
        try:
            self._exec_run(self._cmdline, info)
        except OSError as exception:
            raise ExecutableCallError(
                f'Error in calling "{self._file}" program.',
            ) from exception


class SubTaskError(Exception):
    """
    SubTask module error.
    """


class TaskKeywordError(Exception):
    """
    Task keyword error.
    """


class ExecutableCallError(SubTaskError):
    """
    Executable call error.
    """


class FileWriteError(SubTaskError):
    """
    File write error.
    """


class OutputWriteError(SubTaskError):
    """
    Output write error.
    """


class PipeNotSupportedError(SubTaskError):
    """
    Pipe '|' not supported error.
    """


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        self.config()
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

    @staticmethod
    def _signal_ignore(
        # pylint: disable=no-member
        _signal: int,
        _frame: types.FrameType,
    ) -> Union[
        Callable[[signal.Signals, types.FrameType], Any],
        int,
        signal.Handlers,
        None,
    ]:
        pass

    @classmethod
    def _filter_background(cls, pattern: str) -> None:
        signal.signal(signal.SIGINT, cls._signal_ignore)
        Task(sys.argv[1:]).run(pattern=pattern)

    @staticmethod
    def _start_daemon(file: str) -> None:
        if os.name == 'posix':
            mypid = os.getpid()
            os.setpgid(mypid, mypid)  # New PGID

        child = Child(sys.argv[1:]).run(error2output=True)
        child.stdin.close()
        if file:
            try:
                with Path(file).open('ab') as ofile:
                    while True:
                        byte = child.stdout.read(1)
                        if not byte:
                            break
                        ofile.write(byte)
                        ofile.flush()  # Unbuffered
            except OSError:
                pass
        else:
            while child.stdout.read(BUFFER_SIZE):
                pass

    def run(self) -> int:
        """
        Start program
        """
        if '_SUBTASK_MOD_BACKGROUND_FILTER' in os.environ:
            pattern = os.environ['_SUBTASK_MOD_BACKGROUND_FILTER']
            del os.environ['_SUBTASK_MOD_BACKGROUND_FILTER']
            self._filter_background(pattern)
        elif '_SUBTASK_MOD_DAEMON_FILE' in os.environ:
            file = os.environ['_SUBTASK_MOD_DAEMON_FILE']
            del os.environ['_SUBTASK_MOD_DAEMON_FILE']
            self._start_daemon(file)
        else:
            help(__name__)

        return 0


if __name__ == '__main__':
    if sys.argv[-1] in ('-v', '-V', '-version', '--version'):
        print(f"Python sub task handling module {RELEASE} ({VERSION})")
    elif '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
