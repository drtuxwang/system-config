#!/usr/bin/env python3
"""
Python sub task handling module

Copyright GPL v2: 2006-2016 By Dr Colin Kong

Version 2.1.0 (2016-08-20)
"""

import copy
import os
import re
import signal
import subprocess
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

BUFFER_SIZE = 131072


class Task(object):
    """
    This class handles running sub process interactively.
    """

    def __init__(self, cmdline):
        """
        cmdline = Command line as a list
        """
        self._file = cmdline[0]
        self._cmdline = cmdline
        if os.name == 'nt':
            if '|' in cmdline:
                raise PipeNotSupportedError('Windows does not support pipes.')
            try:
                with open(cmdline[0], errors='replace') as ifile:
                    if ifile.readline().startswith('#!/usr/bin/env python'):
                        self._cmdline = [sys.executable, '-B'] + cmdline
            except OSError:
                pass
        self._status = {'output': [], 'error': [], 'exitcode': 0}

    def get_cmdline(self):
        """
        Return the command line as a list.
        """
        return self._cmdline

    def get_file(self):
        """
        Return file location
        """
        return self._file

    def has_output(self):
        """
        Return True if stdout used.
        """
        return self._status['output']

    def is_match_output(self, pattern):
        """
        Return True if stdout has pattern.

        pattern = Regular expression
        """
        ispattern = re.compile(pattern)
        for line in self._status['output']:
            if ispattern.search(line):
                return True
        return False

    def get_output(self, pattern=''):
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

    def has_error(self):
        """
        Return True if stderr used.
        """
        return self._status['error']

    def is_match_error(self, pattern):
        """
        Return True if stderr has pattern.

        pattern = Regular expression
        """
        ispattern = re.compile(pattern)
        for line in self._status['error']:
            if ispattern.search(line):
                return True

    def get_error(self, pattern=''):
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

    def get_exitcode(self):
        """
        Return exitcode of run.
        """
        return self._status['exitcode']

    @staticmethod
    def _parse_keys(keys, **kwargs):
        if set(kwargs.keys()) - set(keys):
            raise TaskKeywordError(
                'Unsupported keyword "' +
                list(set(kwargs.keys()) - set(keys))[0] + '".'
            )
        info = {}
        for key in keys:
            try:
                info[key] = kwargs[key]
            except KeyError:
                if key in ('file', 'pattern'):
                    info[key] = ''
                else:
                    info[key] = None
        try:
            env = copy.copy(kwargs['env'])
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
    def _send_stdin(child, stdin):
        for line in stdin:
            try:
                child.stdin.write(line.encode('utf-8') + b'\n')
            except OSError:
                break
        child.stdin.close()

    @staticmethod
    def _recv_stdout(child, ismatch, replace):
        while True:
            try:
                line = child.stdout.readline().decode('utf-8', 'replace')
            except (KeyboardInterrupt, OSError):
                break
            if not line:
                break
            if not ismatch or not ismatch.search(line):
                sys.stdout.write(line.replace(replace[0], replace[1]))

    @staticmethod
    def _recv_stderr(child, ismatch, replace):
        while True:
            try:
                line = child.stderr.readline().decode('utf-8', 'replace')
            except (KeyboardInterrupt, OSError):
                break
            if not line:
                break
            if not ismatch or not ismatch.search(line):
                sys.stderr.write(line.replace(replace[0], replace[1]))

    @staticmethod
    def _interactive_run(cmdline, info):
        if '|' in cmdline:
            pipe = True
            cmdline = subprocess.list2cmdline(cmdline)
        else:
            pipe = False

        try:
            return subprocess.call(cmdline, env=info['env'], shell=pipe)
        except KeyboardInterrupt:
            return 130

    @staticmethod
    def _start_child(cmdline, info):
        if '|' in cmdline:
            pipe = True
            cmdline = subprocess.list2cmdline(cmdline)
        else:
            pipe = False

        if info['error2output']:
            stderr = subprocess.STDOUT
        else:
            stderr = subprocess.PIPE
        return subprocess.Popen(
            cmdline,
            env=info['env'],
            shell=pipe,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=stderr
        )

    def _interactive_child_run(self, cmdline, info):
        child = self._start_child(cmdline, info)
        if info['stdin']:
            self._send_stdin(child, info['stdin'])

        if info['pattern']:
            ismatch = re.compile(info['pattern'])
        else:
            ismatch = None
        if not info['replace']:
            info['replace'] = ('', '')
        try:
            self._recv_stdout(child, ismatch, info['replace'])
        except OSError:
            raise OutputWriteError(
                'Error writing stderr of "' + self._file + '" program.'
            )
        if not info['error2output']:
            try:
                self._recv_stderr(child, ismatch, info['replace'])
            except OSError:
                raise OutputWriteError(
                    'Error  writing output of "' + self._file + '" program.')
        return child.wait()

    def run(self, **kwargs):
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
            'directory', 'env', 'error2output', 'pattern',
            'replace', 'stdin'), **kwargs)

        if not sys.stdout.isatty():
            sys.stdout.flush()
        if not sys.stderr.isatty():
            sys.stderr.flush()
        if info['directory']:
            pwd = os.getcwd()
            os.chdir(info['directory'])
        try:
            if (info['error2output'] or info['pattern'] or
                    info['replace'] or info['stdin']):
                self._status['exitcode'] = self._interactive_child_run(
                    self._cmdline, info)
            else:
                self._status['exitcode'] = self._interactive_run(
                    self._cmdline, info)
        except OSError:
            raise ExecutableCallError(
                'Error in calling "' + self._file + '" program.')
        if info['directory']:
            os.chdir(pwd)
        return self._status['exitcode']


class Background(Task):
    """
    This class handles running sub process in background mode.
    """

    @staticmethod
    def _start_background_run(cmdline, info):
        if '|' in cmdline:
            pipe = True
            cmdline = subprocess.list2cmdline(cmdline)
        else:
            pipe = False

        if info['pattern']:
            os.environ['_SUBTASK_MOD_BACKGROUND_FILTER'] = info['pattern']
            subprocess.Popen(
                [sys.executable, '-B', __file__] + cmdline,
                shell=pipe,
                env=info['env']
            )
            del os.environ['_SUBTASK_MOD_BACKGROUND_FILTER']
        else:
            subprocess.Popen(cmdline, shell=pipe, env=info['env'])

    def run(self, **kwargs):
        """
        Start background process.

        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        error2output = Flag to send stderr to stdout
        pattern = Regular expression for removing output
        """
        info = self._parse_keys(
            ('directory', 'env', 'error2output', 'pattern'),
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
        except OSError:
            raise ExecutableCallError(
                'Error in calling "' + self._file + '" program.')
        if info['directory']:
            os.chdir(pwd)


class Batch(Task):
    """
    This class handles running sub process in batch mode.
    """

    @staticmethod
    def _write_file(child, file, append):
        if append:
            mode = 'ab'
        else:
            mode = 'wb'
        try:
            with open(file, mode) as ofile:
                while True:
                    chunk = child.stdout.read(4096)
                    if not len(chunk):
                        break
                    ofile.write(chunk)
        except KeyboardInterrupt:
            pass
        except OSError:
            if append:
                raise OutputWriteError(
                    'Cannot append to "' + file + '" output file.'
                )
            else:
                raise OutputWriteError(
                    'Cannot create "' + file + '" output file.'
                )

    def _batch_run(self, cmdline, info):
        child = self._start_child(cmdline, info)
        if info['stdin']:
            self._send_stdin(child, info['stdin'])

        ismatch = re.compile(info['pattern'])
        file = info['file']
        if file:
            self._write_file(child, info['file'], info['append'])
        else:
            while True:
                try:
                    line = child.stdout.readline().decode(
                        'utf-8', 'replace')
                except (KeyboardInterrupt, OSError):
                    break
                if not line:
                    break
                if ismatch.search(line):
                    self._status['output'].append(
                        line.rstrip('\r\n'))
        if not info['error2output']:
            while True:
                try:
                    line = child.stderr.readline().decode(
                        'utf-8', 'replace')
                except (KeyboardInterrupt, OSError):
                    break
                if not line:
                    break
                if ismatch.search(line):
                    self._status['error'].append(line.rstrip('\r\n'))
        return child.wait()

    def run(self, **kwargs):
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
            'append', 'directory', 'env', 'error2output',
            'file', 'pattern', 'stdin'
        ), **kwargs)

        if info['directory']:
            pwd = os.getcwd()
            os.chdir(info['directory'])
        try:
            self._status['exitcode'] = self._batch_run(
                self._cmdline, info)
        except OSError:
            raise ExecutableCallError(
                'Error in calling "' + self._file + '" program.'
            )
        if info['directory']:
            os.chdir(pwd)

        return self._status['exitcode']


class Child(Task):
    """
    This class handles running sub process as a child process.
    """

    def run(self, **kwargs):
        """
        Return child process object with stdin, stdout and stderr pipes.

        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        error2output = Flag to send stderr to stdout
        """
        info = self._parse_keys(('directory', 'env', 'error2output'), **kwargs)

        if info['directory']:
            pwd = os.getcwd()
            os.chdir(info['directory'])
        try:
            return self._start_child(self._cmdline, info)
        except OSError:
            raise ExecutableCallError(
                'Error in calling "' + self._file + '" program.'
            )
        if info['directory']:
            os.chdir(pwd)


class Daemon(Task):
    """
    This class handles running sub process as a daemon.
    """

    @staticmethod
    def _start_daemon(cmdline, info):
        if '|' in cmdline:
            pipe = True
            cmdline = subprocess.list2cmdline(cmdline)
        else:
            pipe = False

        os.environ['_SUBTASK_MOD_DAEMON_FILE'] = info['file']
        subprocess.Popen(
            [sys.executable, '-B', __file__] +
            cmdline, shell=pipe, env=info['env']
        )
        del os.environ['_SUBTASK_MOD_DAEMON_FILE']

    def run(self, **kwargs):
        """
        Replace current process with new executable.

        directory = Directory to run command in
        env = Dictionary containing environmental variables to change
        file =  Log stdout & stderr to file
        """
        info = self._parse_keys(('directory', 'env', 'file'), **kwargs)

        if info['directory']:
            pwd = os.getcwd()
            os.chdir(info['directory'])
        try:
            self._start_daemon(self._cmdline, info)
        except OSError:
            raise ExecutableCallError(
                'Error in calling "' + self._file + '" program.'
            )
        if info['directory']:
            os.chdir(pwd)


class Exec(Task):
    """
    This class handles replaces current process with new executable.
    """

    @staticmethod
    def _windows_exec_run(cmdline, info):
        # pylint: disable = no-member
        stdout_write = sys.stdout.buffer.write
        stderr_write = sys.stderr.buffer.write
        # pylint: enable = no-member
        try:
            child = subprocess.Popen(
                cmdline,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=info['env']
            )
            byte = True
            while byte:
                byte = child.stdout.read(1)
                stdout_write(byte)
                sys.stdout.flush()
            byte = True
            while byte:
                byte = child.stderr.read(1)
                stderr_write(byte)
                sys.stderr.flush()
            exitcode = child.wait()
        except OSError:
            exitcode = 1
        raise SystemExit(exitcode)

    @classmethod
    def _exec_run(cls, cmdline, info):
        if '|' in cmdline:
            raise PipeNotSupportedError('Exec does not support pipe.')

        if os.name == 'nt':  # Avoids Windows execvpn exit status bug
            cls._windows_exec_run(cmdline, info)
        else:
            os.execvpe(cmdline[0], cmdline, env=info['env'])

    def run(self, **kwargs):
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
        except OSError:
            raise ExecutableCallError(
                'Error in calling "' + self._file + '" program.')


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


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self.config()
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

    @staticmethod
    def _signal_ignore(sig, frame):
        pass

    @classmethod
    def _filter_background(cls, pattern):
        signal.signal(signal.SIGINT, cls._signal_ignore)
        Task(sys.argv[1:]).run(pattern=pattern)

    @staticmethod
    def _start_daemon(file):
        if os.name == 'posix':
            mypid = os.getpid()
            os.setpgid(mypid, mypid)  # New PGID

        child = Child(sys.argv[1:]).run(error2output=True)
        child.stdin.close()
        if file:
            try:
                with open(file, 'ab') as ofile:
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

    def run(self):
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


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
