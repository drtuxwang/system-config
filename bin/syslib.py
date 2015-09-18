#!/usr/bin/env python3
"""
Python system interaction Library

2006-2015 By Dr Colin Kong

Version 5.0 (2015-06-02)
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import collections
import copy
import distutils.version
import glob
import os
if os.name == "nt":
    import platform
import re
import shutil
import signal
import socket
import subprocess
import time


class Dump(object):
    """
    This class provides a "dump()" method for printing all object attributes.
    """

    def dump(self, prefix="self."):
        """
        Dump object recursively.

        prefix = Object address (ie "myobject.subobject.")
        """
        if not prefix.endswith("."):
            prefix += "."

        self._dumpAttributes(prefix, [])

    def dumpValue(self, prefix, dumped, value):
        """
        Print attribute value.

        prefix = Object address (ie "myobject.subobject")
        dumped = List of dumped object addresses
        value  = Python dumpable or basic object
        """
        if self._isDumpable(value):
            value._dumpAttributes(prefix + ".", dumped)
        elif type(value) == str:
            print(prefix, '= "' + value.replace("\\", "\\\\").replace('"', '\\"') + '"')
        else:
            print(prefix, "=", value)

    def _dumpAttributes(self, prefix, dumped):
        """
        Dump all attributes.

        prefix = Object address (ie "myobject.subobject.")
        dumped = List of dumped object addresses
        """
        address = hex(id(self))
        dumped.append(address)
        nref = dumped.count(address)

        if nref == 1:
            print(prefix, self)
            for attribute in sorted(self.__dict__.keys()):
                value = self.__dict__[attribute]
                if type(value) in (dict, list, tuple, set) and self._hasContainer(value):
                    self._dumpContainer(prefix, dumped, attribute, value)
                else:
                    self.dumpValue(prefix + attribute, dumped, value)
        else:
            print(prefix, str(self).replace(">", " reference " + str(nref) + ">"))

    def _dumpContainer(self, prefix, dumped, name, data):
        """
        Dumps contents of dict, list, tuple or set object.

        prefix = Object address (ie "myobject.subobject.")
        dumped = List of dumped object addresses
        name   = Python attribute name
        data   = Python dict, list, tuple or set object
        """
        dataT = type(data)

        if dataT == dict:
            print(prefix + name, "<dict object at", hex(id(self)) + ">")
            for key in sorted(data.keys()):
                self.dumpValue(prefix + name + "[" + str(key) + "]", dumped, data[key])

        elif dataT == list:
            print(prefix + name, "<list object at", hex(id(self)) + ">")
            for i in range(len(data)):
                self.dumpValue(prefix + name + "[" + str(i) + "]", dumped, data[i])

        elif dataT == tuple:
            print(prefix + name, "<tuple object at", hex(id(self)) + ">")
            for i in range(len(data)):
                self.dumpValue(prefix + name + "[" + str(i) + "]", dumped, data[i])

        elif dataT == set:
            print(prefix + name, "<set object at", hex(id(self)) + ">")
            for item in data:
                self.dumpValue(prefix + name + "[]", dumped, item)

        else:
            raise NotImplementedError

    def _hasContainer(self, data):
        """
        Returns True if data is container and contains dumpable object, dict, list,
        tuple or set object.

        data = Python data object
        """
        if type(data) == dict:
            for key in data.keys():
                value = data[key]
                if self._isDumpable(value) or type(value) in (dict, list, value, set):
                    return True
        elif type(data) in (list, tuple, set):
            for value in data:
                if self._isDumpable(value):
                    return True
        return False

    def _isDumpable(self, data):
        """
        Return True if data has "dump()" method.

        data = Any Python data object
        """
        return (hasattr(data.__class__, "dump") and
                isinstance(getattr(data.__class__, "dump"), collections.Callable))


class Background:
    """
    This class starts a command as a background process.
    """

    def __init__(self):
        filter = os.environ["_SYSTEM_BG"]
        del os.environ["_SYSTEM_BG"]
        signal.signal(signal.SIGINT, self._signalIgnore)
        try:
            Command(file=sys.argv[1], args=sys.argv[2:]).run(filter=filter)
        except SyslibError:
            pass

    def _signalIgnore(self, signal, frame):
        pass


class Command(Dump):
    """
    This class contains a command which consists of file, flags and args.

    self._program  = Program name
    self._file     = File location
    self._wrapper  = Wrapper program command
    self._flags    = List of flags for command
    self._args     = List of arguments for command
    self._stdout   = Stdout for batch process
    self._stderr   = Stderr for batch process
    self._exitcode = Exitcode
    """

    def __init__(self, program="", cmd="", file="", flags=None, args=None, pathextra=[],
                 platform="", check=True):
        """
        program   = Command program name (ie "evince", "bin/acroread")
        file      = Optional command file location (avoids searching)
        flags     = Optional command flags list
        args      = Optional command arguments list
        cmd       = Program and args list supplied as command string
        pathextra = Optional extra PATH to prefix in search
        platform  = Optional platform (ie "windows-x86_64" for WINE)
        check     = Whether to stop if command file not found
        """
        self._program = program
        self._wrapper = []
        self._file = file

        if flags is None:
            self._flags = []
        else:
            self._flags = flags

        if cmd:
            args = self._cmd2args(cmd)
            self._program = args[0]
            self._args = args[1:]
        elif args is None:
            self._args = []
        else:
            self._args = args

        self._stdout = ""
        self._stderr = ""
        self._exitcode = 0

        if self._program and not file:
            if (os.sep in self._program and os.path.isfile(self._program) and
                    not sys.argv[0].endswith(self._program + ".py")):
                self._file = self._program
            else:
                self._locate(pathextra, platform, check)

    def run(
            self, directory=None, env=None, filter="", logfile="", mode="interactive",
            replace=("", ""), pipes=(), stdin=[], error2output=False, outputFile="",
            append=False):
        """
        directory    = <directory>   - Directory to run command in
        env          = <dictonary>   - Dictionary containing environmental variables to change
                                       (not for unfiltered interactive)
        filter       = <pattern>     - Regular expression filtering/selection.
        logfile      = <file>        - Redirect stdout/stderr to log file (daemon mode only).
        mode         = "batch"       - Run as a batch process and return output matching filter.
        mode         = "background"  - Run as background process with optional filtering.
        mode         = "child"       - Return child process object with stdin, stdout
                                       and stderr pipes.
        mode         = "daemon"      - Run as a background daemon and log or forget all output.
        mode         = "exec"        - Run as replacement of current process.
        mode         = "interactive" - Run interactively with optional filtering/replacement.
        replace      = (str1, str2)  - Replace all occurance of str1 with str2
                                       (interactive mode only).
        pipes        = [Command]     - Command class objects to form execution pipe
                                       (not child, exec or filtered background modes).
        stdin        = <lines>       - Stdin input text (interactive and batch only).
        error2output = True          - Send stderr to stdout
                                       (not exec or unfiltered interactive modes).
        outputFile   = <file>        - Redirect stdout to file (batch mode only).
        append       = True          - Append to outputFile (batch mode only).
        """
        if not sys.stdout.isatty():
            sys.stdout.flush()
        if not sys.stderr.isatty():
            sys.stderr.flush()

        if directory:
            pwd = os.getcwd()
            os.chdir(directory)

        self._stdout = []
        self._stderr = []
        self._exitcode = 0
        if error2output:
            stderr = subprocess.STDOUT
        else:
            stderr = subprocess.PIPE

        if pipes:
            pipe = True
            cmdline = subprocess.list2cmdline(self.getCommandLine())
            for cmd in pipes:
                cmdline += " | " + subprocess.list2cmdline(cmd.getCommandLine())
        else:
            pipe = False
            cmdline = self.getCommandLine()

        if env is not None:
            env = copy.copy(env)
            for key in os.environ.keys():
                if key not in env.keys():
                    env[key] = os.environ[key]
                elif env[key] is None:
                    del env[key]
            for key in env.keys():
                if env[key] is None:
                    del env[key]

        if mode == "background":
            try:
                if filter:
                    os.environ["_SYSTEM_BG"] = filter
                    if env is None:
                        child = subprocess.Popen([sys.executable, __file__] + cmdline, shell=pipe)
                    else:
                        child = subprocess.Popen([sys.executable, __file__] + cmdline,
                                                 shell=pipe, env=env)
                    del os.environ["_SYSTEM_BG"]
                elif env is None:
                    child = subprocess.Popen(cmdline, shell=pipe)
                else:
                    child = subprocess.Popen(cmdline, shell=pipe, env=env)
            except OSError as exception:
                self._oserror(exception)

        elif mode == "exec":
            if os.name == "nt":  # Avoids Windows execvpn exit status bug
                stdoutWrite = sys.stdout.buffer.write
                stderrWrite = sys.stderr.buffer.write
                try:
                    if env == {}:
                        child = subprocess.Popen(cmdline, shell=False, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)
                    else:
                        child = subprocess.Popen(cmdline, shell=False, stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE, env=env)
                    byte = True
                    while byte:
                        byte = child.stdout.read(1)
                        stdoutWrite(byte)
                        sys.stdout.flush()
                    byte = True
                    while byte:
                        byte = child.stderr.read(1)
                        stderrWrite(byte)
                        sys.stderr.flush()
                    exitcode = child.wait()
                except OSError:
                    exitcode = 1
                raise SystemExit(exitcode)  # Here we are exiting as exec fails on Windows
            try:
                if env == {}:
                    os.execvpe(cmdline[0], cmdline, os.environ)
                else:
                    os.execvpe(cmdline[0], cmdline, env)
            except OSError as exception:
                self._oserror(exception)

        elif mode == "daemon":
            os.environ["_SYSTEM_DM"] = logfile
            if env is None:
                child = subprocess.Popen([sys.executable, __file__] + cmdline, shell=pipe)
            else:
                child = subprocess.Popen([sys.executable, __file__] + cmdline, shell=pipe, env=env)
            del os.environ["_SYSTEM_DM"]

        elif mode == "interactive" and not filter and replace == ("", "") and not stdin:
            try:
                if env is None:
                    self._exitcode = subprocess.call(cmdline, shell=pipe)
                else:
                    self._exitcode = subprocess.call(cmdline, shell=pipe, env=env)
            except KeyboardInterrupt:
                self._exitcode = 130
            except OSError as exception:
                self._oserror(exception)

        else:
            try:
                if env is None:
                    child = subprocess.Popen(cmdline, shell=pipe, stdout=subprocess.PIPE,
                                             stderr=stderr, stdin=subprocess.PIPE)
                else:
                    child = subprocess.Popen(cmdline, shell=pipe, stdout=subprocess.PIPE,
                                             stderr=stderr, stdin=subprocess.PIPE, env=env)
            except OSError as exception:
                self._oserror(exception)
            if mode == "child":
                if directory:
                    os.chdir(pwd)
                return child
            for line in stdin:
                try:
                    child.stdin.write(line.encode("utf-8") + b"\n")
                except IOError:
                    break
            child.stdin.close()
            isfilter = re.compile(filter)

            if mode in ("background", "interactive"):
                while True:
                    try:
                        line = child.stdout.readline().decode("utf-8", "replace")
                    except (IOError, KeyboardInterrupt):
                        break
                    if not line:
                        break
                    if not filter or not isfilter.search(line):
                        try:
                            sys.stdout.write(line.replace(replace[0], replace[1]))
                        except IOError:
                            raise SyslibError(sys.argv[0] + ': Error in writing stdout of "' +
                                              self._file + '" program.')
                while True:
                    try:
                        line = child.stderr.readline().decode("utf-8", "replace")
                    except (IOError, KeyboardInterrupt):
                        break
                    if not line:
                        break
                    if not filter or not isfilter.search(line):
                        sys.stdout.write(line.replace(replace[0], replace[1]))

            elif mode == "batch":
                if outputFile:
                    if append:
                        try:
                            ofile = open(outputFile, "ab")
                        except IOError:
                            raise SyslibError(sys.argv[0] + ': Cannot append to "' +
                                              outputFile + '" output file.')
                    else:
                        try:
                            ofile = open(outputFile, "wb")
                        except IOError:
                            raise SyslibError(sys.argv[0] + ': Cannot create "' +
                                              outputFile + '" output file.')
                    while True:
                        try:
                            chunk = child.stdout.read(4096)
                        except KeyboardInterrupt:
                            break
                        if not len(chunk):
                            ofile.close()
                            break
                        ofile.write(chunk)
                else:
                    while True:
                        try:
                            line = child.stdout.readline().decode("utf-8", "replace")
                        except (IOError, KeyboardInterrupt):
                            break
                        if not line:
                            break
                        if isfilter.search(line):
                            self._stdout.append(line.rstrip("\r\n"))
                if not error2output:
                    while True:
                        try:
                            line = child.stderr.readline().decode("utf-8", "replace")
                        except (IOError, KeyboardInterrupt):
                            break
                        if not line:
                            break
                        if isfilter.search(line):
                            self._stderr.append(line.rstrip("\r\n"))

            else:
                raise SyslibError(sys.argv[0] +
                                  ': "syslib.Command()" invalid run mode "' + mode + '".')

            self._exitcode = child.wait()

        if directory:
            os.chdir(pwd)

    def args2cmd(self, args):
        """
        Join arguments list into command string.

        args = List of arguments
        """
        return subprocess.list2cmdline(args)

    def cmd2args(self, cmd):
        """
        Split command string into arguments list.
        """
        chars = []
        backslashs = ""

        for char in cmd:
            if char == '\\':
                backslashs += char
            elif char == '"' and backslashs:
                nbackslashs = len(backslashs)
                chars.extend(["\\"] * (nbackslashs//2))
                backslashs = ""
                if nbackslashs % 2:
                    chars.append(1)
                else:
                    chars.append('"')
            else:
                if backslashs:
                    chars.extend(list(backslashs))
                    backslashs = ""
                chars.append(char)

        args = []
        arg = []
        quoted = False
        chars.append(" ")
        for char in chars:
            if char == '"':
                quoted = not quoted
            elif char == 1:
                arg.append('"')
            elif char in (' ', '\t'):
                if quoted:
                    arg.append(char)
                else:
                    if arg:
                        args.append(''.join(arg))
                        arg = []
            else:
                arg.append(char)

        return args

    def isFound(self):
        """
        Return True if file is defined.
        """
        return self._file != ""

    def getProgram(self):
        """
        Return program name.
        """
        return self._program

    def getFile(self):
        """
        Return file location.
        """
        return self._file

    def getFlags(self):
        """
        Return list of flags.
        """
        return self._flags

    def setFlags(self, flags):
        """
        Set command line flags

        flags = List of flags
        """
        self._flags = flags

    def appendFlag(self, flag):
        """
        Append to command line flags

        flag = Flag
        """
        self._flags.append(flag)

    def extendFlags(self, flags):
        """
        Extend command line flags

        flags = List of flags
        """
        self._flags.extend(flags)

    def getArgs(self):
        """
        Return list of arguments.
        """
        return self._args

    def setArgs(self, args):
        """
        Set command line arguments

        args = List of arguments
        """
        self._args = args

    def appendArg(self, arg):
        """
        Append to command line arguments

        arg = Argument
        """
        self._args.append(arg)

    def extendArgs(self, args):
        """
        Extend command line arguments

        args = List of arguments
        """
        self._args.extend(args)

    def setWrapper(self, command):
        """
        Set wrapper program for command.

        command = Wrapper program's Command class object
        """
        if not command.isFound():
            raise SyslibError(sys.argv[0] + ': Cannot set blank wrapper program for "' +
                              self._file + '" program.')
        self._wrapper = command.getCommandLine()

    def getCommandLine(self):
        """
        Return the command line as a list.
        """
        if os.name == "nt":
            try:
                ifile = open(self._file, "rb")
            except IOError:
                pass
            else:
                line = ifile.readline().decode("utf-8", "replace").rstrip("\r\n")
                ifile.close()
                if line.startswith("#!/"):
                    wrapper = line.replace("#!/usr/bin/env ", "").split()
                    if wrapper[0].startswith("python"):
                        return [sys.executable, self._file] + self._flags + self._args
                    elif wrapper:
                        return ([Command(wrapper[0].split("/")[-1],
                                args=wrapper[1:]).getCommandLine()] + self._wrapper +
                                [self._file] + self._flags+self._args)

        return self._wrapper + [self._file] + self._flags + self._args

    def getExitcode(self):
        """
        Return exitcode of run.
        """
        return self._exitcode

    def hasOutput(self):
        """
        Return True if stdout used.
        """
        return self._stdout != []

    def isMatchOutput(self, pattern):
        """
        Return True if stdout has pattern.

        pattern = Regular expression
        """
        ispattern = re.compile(pattern)
        for line in self._stdout:
            if ispattern.search(line):
                return True
        return False

    def getOutput(self, pattern=""):
        """
        Return list of lines in stdout that match pattern. If no pattern return all.

        pattern = Regular expression
        """
        if pattern == "":
            return self._stdout

        stdout = []
        ispattern = re.compile(pattern)
        for line in self._stdout:
            if ispattern.search(line):
                stdout.append(line)
        return stdout

    def hasError(self):
        """
        Return True if stderr used.
        """
        return self._stderr != []

    def isMatchError(self, pattern):
        """
        Return True if stderr has pattern.

        pattern = Regular expression
        """
        ispattern = re.compile(pattern)
        for line in self._stderr:
            if ispattern.search(line):
                return True

    def getError(self, pattern=""):
        """
        Return list of lines in stderr that match pattern. If no pattern return all.

        pattern = Regular expression
        """
        if pattern == "":
            return self._stderr

        stderr = []
        ispattern = re.compile(pattern)
        for line in self._stderr:
            if ispattern.search(line):
                stderr.append(line)
        return stderr

    def _checkGlibc(self, files):
        hasGlibc = re.compile("-glibc_\d+[.]\d+([.]\d+)?")
        nfiles = []
        for file in files:
            if hasGlibc.search(file):
                version = file.split("-glibc_")[1].split("-")[0].split("/")[0]
                if (distutils.version.LooseVersion(self._getGlibc()) >=
                        distutils.version.LooseVersion(version)):
                    nfiles.append(file)
            else:
                nfiles.append(file)
        return nfiles

    def _getGlibc(self):
        """
        Return glibc version string
        (based on glibc version used to compile "ldd" or return "0.0" for non Linux)
        """
        if "glibc" not in _cache.keys():
            if _cache["osname"] == "linux":
                ldd = Command("ldd", args=["--version"], check=False)
                if ldd.isFound():
                    ldd.run(filter="^ldd ", mode="batch")
                    _cache["glibc"] = ldd.getOutput()[0].split()[-1]
                else:
                    raise SyslibError(sys.argv[0] + ': Cannot find "ldd" command.')
            else:
                _cache["glibc"] = "0.0"

        return _cache["glibc"]

    def _locate(self, pathextra, platform, check):
        if not platform:
            platform = info.getPlatform()

        if platform in ("windows-x86_64", "windows-x86"):
            extensions = ["", ".py"]
            if "PATHEXT" in os.environ.keys():
                extensions.extend(os.environ["PATHEXT"].lower().split(os.pathsep))
        else:
            extensions = [""]

        directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        if os.path.basename(directory) == "bin":
            directory = os.path.dirname(directory)
            files = []

            if platform in ("linux-x86_64", "linux-x86"):
                if platform == "linux-x86_64":
                    files = self._checkGlibc(glob.glob(os.path.join(directory, "*",
                                             "linux64_*-x86*", self._program)))
                if not files:
                    files = self._checkGlibc(glob.glob(os.path.join(directory, "*",
                                             "linux_*-x86*", self._program)))

            elif platform in ("macos-x86_64", "macos-x86"):
                if platform == "macos-x86_64":
                    files = glob.glob(os.path.join(directory, "*", "macos64_*-x86*", self._program))
                if not files:
                    files = glob.glob(os.path.join(directory, "*", "macos_*-x86*", self._program))

            elif platform in ("sunos-x86_64", "sunos-x86"):
                if platform == "sunos-x86_64":
                    files = glob.glob(os.path.join(directory, "*", "sunos64_*-x86*", self._program))
                if not files:
                    files = glob.glob(os.path.join(directory, "*", "sunos_*-x86*", self._program))

            elif platform in ("windows-x86_64", "windows-x86"):
                if platform in ("windows-x86_64"):
                    for extension in extensions:
                        files = glob.glob(os.path.join(directory, "*",
                                          "windows64_*-x86*", self._program + extension))
                        if files:
                            break
                if not files:
                    for extension in extensions:
                        files = glob.glob(os.path.join(directory, "*",
                                                       "windows_*-x86*", self._program + extension))
                        if files:
                            break

            # Search directories with 4 or more characters as fall back for local port
            if not files:
                for extension in extensions:
                    files = glob.glob(os.path.join(directory, "????*",
                                      self._program + extension))
                    if files:
                        break

            self._file = info.newest(files)
            if self._file:
                return

        # Shake PATH to make it unique
        paths = []
        for path in os.environ["PATH"].split(os.pathsep):
            if path:
                if path not in paths:
                    paths.append(path)

        # Prevent recursion
        program = os.path.basename(self._program)
        if os.path.basename(sys.argv[0]) in (program, program + ".py"):
            mydir = os.path.dirname(sys.argv[0])
            if mydir in paths:
                paths = paths[paths.index(mydir) + 1:]

        # Search PATH
        if sys.argv[0].endswith(".py"):
            mynames = (sys.argv[0][:-3], sys.argv[0])
        else:
            mynames = (sys.argv[0], sys.argv[0] + ".py")
        for directory in pathextra + paths:
            if os.path.isdir(directory):
                for extension in extensions:
                    file = os.path.join(directory, program) + extension
                    if os.path.isfile(file):
                        if file not in mynames:
                            self._file = file
                            return
        if check:
            raise SyslibError(sys.argv[0] + ': Cannot find required "' + program + '" software.')

    def _oserror(self, exception):
        if "No such file" in exception.args[1]:
            raise SyslibError(sys.argv[0] + ': Cannot find "' + self._file + '" program.')
        elif "Permission denied" in exception.args:
            raise SyslibError(sys.argv[0] + ': Cannot execute "' + self._file + '" program.')
        raise SyslibError(sys.argv[0] + ': Error in calling "' + self._file + '" program.')


class Daemon:
    """
    This class starts a command as a daemon de-coupled from the current process.
    """

    def __init__(self):
        self._bufferSize = 131072

        logfile = os.environ["_SYSTEM_DM"]
        del os.environ["_SYSTEM_DM"]
        mypid = os.getpid()
        if os.name == "posix":
            os.setpgid(mypid, mypid)  # New PGID
        try:
            child = Command(file=sys.argv[1],
                            args=sys.argv[2:]).run(mode="child", error2output=True)
        except OSError as exception:
            if "No such file" in exception.args[1]:
                raise SyslibError(sys.argv[0] + ': Cannot find "' + sys.argv[1] + '" program.')
            elif "Permission denied" in exception.args:
                raise SyslibError(sys.argv[0] + ': Cannot execute "' + sys.argv[1] + '" program.')
            raise SyslibError(sys.argv[0] + ': Error in calling "' + sys.argv[1] + '" program.')
        child.stdin.close()
        if logfile:
            self._runLog(child, logfile)
        else:
            self._runWait(child)

    def _runLog(self, child, logfile):
        try:
            with open(logfile, "ab") as ofile:
                while True:
                    byte = child.stdout.read(1)
                    if not byte:
                        break
                    ofile.write(byte)
                    ofile.flush()  # Unbuffered
        except IOError:
            pass

    def _runWait(self, child):
        while child.stdout.read(self._bufferSize):
            pass


class FileStat(Dump):
    """
    This class contains file status information.

    self._file  = Filename
    self._mode  = Inode protection mode
    self._ino   = Inode number
    self._dev   = Device inode resides on
    self._nlink = Number of links to the inode
    self._uid   = User ID of the owner
    self._gid   = Group ID of the owner.
    self._size  = Size in bytes of a file
    self._atime = Time of last access
    self._mtime = Time of last modification
    self._ctime = Time of creation
    """

    def __init__(self, file="", size=None):
        """
        file = filename

        size = Override file size (useful for zero sizing links)
        """
        if file:
            self._file = file
            try:
                (self._mode, self._ino, self._dev, self._nlink, self._uid, self._gid,
                    self._size, self._atime, self._mtime, self._ctime) = os.stat(file)
            except (OSError, TypeError):
                if not os.path.islink:
                    raise SyslibError(sys.argv[0] + ': Cannot find "' + file + '" file status.')
                (self._mode, self._ino, self._dev, self._nlink, self._uid, self._gid, self._size,
                    self._atime, self._mtime, self._ctime) = [0] * 10
            else:
                if size is not None:
                    self._size = size

    def dumpValue(self, prefix, dumped, value):
        """
        Print contents of object (overrides default for "_mode")

        prefix = Object address (ie "myobject.subobject")
        dumped = List of dumped object addresses
        value  = Python dumpable or basic object
        """
        if prefix.endswith("._mode"):
            print(prefix, "=", oct(value))
        else:
            super().dumpValue(prefix, dumped, value)

    def getFile(self):
        """
        Return filename
        """
        return self._file

    def getGroupid(self):
        """
        Return group ID of the owner
        """
        return self._gid

    def getInodeDevice(self):
        """
        Return device inode resides on
        """
        return self._dev

    def getInodeNumber(self):
        """
        Return inode number
        """
        return self._ino

    def getNumberlinks(self):
        """
        Return number of links to the inode
        """
        return self._nlink

    def getMode(self):
        """
        Return inode protection mode
        """
        return self._mode

    def getSize(self):
        """
        Return size in bytes of a file
        """
        return self._size

    def getUserid(self):
        """
        Return user ID of the owner
        """
        return self._uid

    def getTime(self):
        """
        Return time of last modification
        """
        return self._mtime

    def getTimeAccess(self):
        """
        Return time of last access
        """
        return self._atime

    def getTimeCreate(self):
        """
        Return time of creation.
        """
        return self._ctime

    def getTimeLocal(self):
        """
        Return time of last modification in full ISO local time format (ie "2011-12-31-12:30:28")
        """
        return time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(self._mtime))


class SystemInfo(Dump):
    """
    This class determines system information.
    The "__name__.info" object is a instance of SystemInfo.
    """

    def __init__(self):
        self._islabel = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)

        if "osname" not in _cache.keys():
            _cache["osname"] = "Unknown"
            _cache["machine"] = "Unknown"

            if os.name == "nt":
                _cache["osname"] = "windows"
                self._isenvName = re.compile("^\w+$", re.IGNORECASE)
                if "PROCESSOR_ARCHITECTURE" in os.environ.keys():
                    if os.environ["PROCESSOR_ARCHITECTURE"] == "AMD64":
                        _cache["machine"] = "x86_64"
                    elif ("PROCESSOR_ARCHITEW6432" in os.environ.keys() and
                            os.environ["PROCESSOR_ARCHITEW6432"] == "AMD64"):
                        _cache["machine"] = "x86_64"
                    elif os.environ["PROCESSOR_ARCHITECTURE"] == "x86":
                        _cache["machine"] = "x86"
                    # This is ok but avoid platform module for other things
                    _cache["kernel"] = platform.version()

            elif os.name == "posix":
                osname, _cache["hostname"], _cache["kernel"], release, arch = os.uname()
                _cache["osname"] = osname.replace("-", "").lower()
                self._isenvName = re.compile("^[A-Z_]\w*$", re.IGNORECASE)

                if _cache["osname"].startswith("cygwin"):
                    if arch == "x86_64":
                        _cache["machine"] = "x86_64"
                    elif re.search("i.86", arch):
                        if "WOW64" in _cache["osname"]:
                            _cache["machine"] = "x86_64"
                        else:
                            _cache["machine"] = "x86"
                    _cache["osname"] = "windows"
                    registryKey = ("/proc/registry/HKEY_LOCAL_MACHINE/SOFTWARE/"
                                   "Microsoft/Windows NT/CurrentVersion")
                    try:
                        with open(os.path.join(registryKey, "CurrentVersion"),
                                  errors="replace") as ifile:
                            _cache["kernel"] = ifile.readline()
                        with open(os.path.join(registryKey, "CurrentBuildNumber"),
                                  errors="replace") as ifile:
                            _cache["kernel"] += "." + ifile.readline()
                    except IOError:
                        raise SyslibError(sys.argv[0] + ': Error reading "' +
                                          registryKey + '" registry key.')

                elif _cache["osname"] == "Darwin":
                    _cache["osname"] = "macos"
                    if arch == "x86_64":
                        _cache["machine"] = "x86_64"
                    elif arch == "i386":
                        sysctl = Command(file="/usr/sbin/sysctl", args=["-a"])
                        sysctl.run(filter="hw.cpu64bit_capable: 1", mode="batch")
                        if sysctl.hasOutput():
                            _cache["machine"] = "x86_64"
                        else:
                            _cache["machine"] = "x86"

                elif _cache["osname"] == "linux":
                    if arch == "ppc64":
                        _cache["machine"] = "power64"
                    elif arch == "sparc64":
                        _cache["machine"] = "sparc64"
                    elif arch == "x86_64":
                        _cache["machine"] = "x86_64"
                    elif re.search("i.86", arch):
                        _cache["machine"] = "x86"

                elif _cache["osname"] == "sunOS":
                    if arch == "i86pc":
                        if os.path.isdir("/lib/amd64"):
                            _cache["machine"] = "x86_64"
                        else:
                            _cache["machine"] = "x86"
                    else:
                        _cache["machine"] = "sparc64"

            _cache["platform"] = _cache["osname"] + "-" + _cache["machine"]

    def idnaHost(self, host):
        """
        Return hostname in IDNA format.
        """
        return str(host.encode("idna"))[2:-1]

    def newest(self, files):
        """
        Return newest file or directory.

        files = List of files
        """
        nfile = ""
        for file in files:
            if os.path.isfile(file) or os.path.isdir(file):
                if nfile:
                    fileStat = FileStat(file)
                    if fileStat.getTime() > nfileStat.getTime():
                        nfile = file
                        nfileStat = fileStat
                else:
                    nfile = file
                    nfileStat = FileStat(nfile)
        return nfile

    def oldest(self, files):
        """
        Return oldest file or directory.

        files = List of files
        """
        nfile = ""
        for file in files:
            if os.path.isfile(file) or os.path.isdir(file):
                if nfile:
                    fileStat = FileStat(file)
                    if fileStat.getTime() < nfileStat.getTime():
                        nfile = file
                        nfileStat = fileStat
                else:
                    nfile = file
                    nfileStat = FileStat(nfile)
        return nfile

    def strings(self, file, pattern):
        """
        Return first match of pattern in binary file
        """
        isMatch = re.compile(pattern)
        try:
            with open(file, "rb") as ifile:
                string = ""
                while True:
                    data = ifile.read(4096)
                    if len(data) == 0:
                        break
                    for byte in data:
                        if byte > 31 and byte < 127:
                            string += chr(byte)
                        else:
                            if len(string) >= 4:
                                if isMatch.search(string):
                                    return string
                            string = ""
            if len(string) >= 4:
                if isMatch.search(string):
                    return string
        except IOError:
            pass
        return ""

    def isenvName(self, name):
        """
        Return True if valid Environmental variable name.

        name = Environmental variable name
        """
        return self._isenvName.match(name)

    def ishost(self, host):
        """
        Return True if host is a valid hostname, hostname.domain, FQDN or IP v4 address.

        Host label characters must be alphanumeric or "-"
        Host label must have 1-63 characters
        Host label cannot start or end with "-"
        FQDN has max of 255 characters
        Uses Internationalized Domain Names in Applications (IDNA) coding
        """
        host = self.idnaHost(host)
        if len(host) > 255:
            return False
        return all(self._islabel.match(label) for label in host.rstrip(".").split("."))

    def getSystem(self):
        """
        Return system name (ie "linux", "windows")
        """
        return _cache["osname"]

    def getKernel(self):
        """
        Return system kernel version (ie "2.6.32-431.el6.x86_64", "6.1.7601")
        """
        return _cache["kernel"]

    def getMachine(self):
        """
        Return machine type (ie "x86", "x86_64")
        """
        return _cache["machine"]

    def getPlatform(self):
        """
        Return platform name (ie "linux-x86_64", "windows-x86_64)
        """
        return _cache["platform"]

    def getHostname(self):
        """
        Return my hostname.
        """
        if "hostname" not in _cache.keys():
            _cache["hostname"] = socket.gethostname()
        return _cache["hostname"].split(".")[0].lower()

    def getUsername(self):
        """
        Return my username.
        """
        if "username" not in _cache.keys():
            _cache["username"] = "Unknown"
            for environment in ("LOGNAME", "USER", "USERNAME"):
                if environment in os.environ.keys():
                    _cache["username"] = os.environ[environment]
        return _cache["username"]


class SyslibError(Dump, Exception):
    """
    This class handles module exception errors.

    self.args = Arguments
    """

    def __init__(self, message):
        """
        message = Error message
        """
        self.args = (message,)

    def getArgs(self):
        """
        Return arguments
        """
        return self.args


class Task(Dump):
    """
    This class handles system processess.

    self._process  = Dictionary containing process information
    """

    def __init__(self, user=""):
        """
        user = Username or "<all>"
        """
        self._process = {}
        if not user:
            user = info.getUsername()
        ps = self._getps()
        ps.run(mode="batch")
        if ps.getProgram() == "tasklist":
            indice = [0]
            position = 0
            for column in ps.getOutput()[2].split():
                position += len(column) + 1
                indice.append(position)
            for line in ps.getOutput()[3:]:
                process = {}
                process["USER"] = line[indice[6]:indice[7]-1].strip()
                if "\\" in process["USER"]:
                    process["USER"] = process["USER"].split("\\")[1]
                if user in (process["USER"], "<all>"):
                    pid = int(line[indice[1]:indice[2]-1])
                    process["PPID"] = 1
                    process["PGID"] = pid
                    process["PRI"] = "?"
                    process["NICE"] = "?"
                    process["TTY"] = line[indice[2]:indice[3]-1].strip().replace("Tcp#", "")
                    process["MEMORY"] = int(line[indice[4]:indice[5]-1].strip().replace(
                                            ",", "").replace(".", "").replace(" K", ""))
                    process["CPUTIME"] = line[indice[7]:indice[8]-1].strip()
                    process["ETIME"] = "?"
                    process["COMMAND"] = line[indice[0]:indice[1]-1].strip()
                    self._process[pid] = process
        else:
            for line in ps.getOutput()[1:]:
                process = {}
                process["USER"] = line.split()[0]
                if user in (process["USER"], "<all>"):
                    pid = int(line.split()[1])
                    process["PPID"] = int(line.split()[2])
                    process["PGID"] = int(line.split()[3])
                    process["PRI"] = line.split()[4]
                    process["NICE"] = line.split()[5]
                    process["TTY"] = line.split()[6]
                    process["MEMORY"] = int(line.split()[7])
                    process["CPUTIME"] = line.split()[8]
                    process["ETIME"] = line.split()[9]
                    process["COMMAND"] = " ".join(line.split()[10:])
                    self._process[pid] = process

    def pgid2pids(self, pgid):
        """
        Return process ID list with process group ID.

        pgid = Process group ID
        """
        if not isinstance(pgid, int):
            raise SyslibError(sys.argv[0] + ': "' + __name__ +
                              '.Task" invalid pgid type "' + str(pgid) + '".')
        pids = []
        for pid in self.getPids():
            if self._process[pid]["PGID"] == pgid:
                pids.append(pid)
        return sorted(pids)

    def pname2pids(self, pname):
        """
        Return process ID list with program name.

        pname = Program name
        """
        pids = []
        if info.getSystem() == "windows":
            isexist = re.compile("^" + pname + "([.]exe|$)")
        else:
            isexist = re.compile("^(|[^ ]+/)" + pname + "( |$)")
        for pid in self.getPids():
            if isexist.search(self._process[pid]["COMMAND"]):
                pids.append(pid)
        return sorted(pids)

    def killpids(self, pids, signal="KILL"):
        """
        Kill processes by process ID list.

        pids   = List of process IDs
        signal = Signal name to send ("CONT", "KILL", "STOP", "TERM")
        """
        if signal not in ("CONT", "KILL", "STOP", "TERM"):
            raise SyslibError(sys.argv[0] + ': Invalid "' + signal + '" signal name.')
        kill = self._getkill()
        if info.getSystem() != "windows":
            kill.setFlags(["-" + signal])
        for pid in pids:
            if info.getSystem() == "windows":
                kill.extendArgs(["/pid", str(pid)])
            else:
                kill.appendArg(str(pid))
        if kill.getArgs():
            kill.run(mode="batch")

    def killpgid(self, pgid, signal="KILL"):
        """
        Kill processes by process group ID.

        pgids  = List of process group ID
        signal = Signal name to send ("CONT", "KILL", "STOP", "TERM")
        """
        if info.getSystem() == "windows":
            self.killpids([pgid], signal=signal)
        else:
            self.killpids([-pgid], signal=signal)

    def killpname(self, pname, signal="KILL"):
        """
        Kill all processes with program name.

        pname  = Program name
        signal = Signal name to send ("CONT", "KILL", "STOP", "TERM")
        """
        self.killpids(self.pname2pids(pname), signal=signal)

    def haspgid(self, pgid):
        """
        Return True if process with <pgid> process group ID exists.

        pgid = Process group ID
        """
        if not isinstance(pgid, int):
            raise SyslibError(sys.argv[0] + ': "' + __name__ +
                              '.Task" invalid pgid type "' + str(pgid) + '".')
        return self.pgid2pids(pgid) != []

    def haspid(self, pid):
        """
        Return True if process with <pid> process ID exists.

        pid = Process ID
        """
        if not isinstance(pid, int):
            raise SyslibError(sys.argv[0] + ': "' + __name__ +
                              '.Task" invalid pid type "' + str(pid) + '".')
        return pid in self._process.keys()

    def haspname(self, pname):
        """
        Return True if process with program name exists.

        pname = Program name
        """
        return self.pname2pids(pname) != []

    def getAncestorPids(self, pid):
        """
        Return list of ancestor process IDs.

        pid = Process ID
        """
        apids = []
        if pid in self._process.keys():
            ppid = self._process[pid]["PPID"]
            if ppid in self._process.keys():
                apids.extend([ppid] + self.getAncestorPids(ppid))
        return apids

    def getDescendantPids(self, ppid):
        """
        Return list of descendant process IDs.

        pid = Parent process ID
        """
        dpids = []
        if ppid in self._process.keys():
            for pid in sorted(self._process.keys()):
                if self._process[pid]["PPID"] == ppid:
                    dpids.extend([pid] + self.getDescendantPids(pid))
        return dpids

    def getOrphanPids(self, pgid):
        """
        Return list of orphaned process IDs excluding process group leader.

        pgid = Process group ID
        """
        pids = []
        for pid in sorted(self._process.keys()):
            if self._process[pid]["PGID"] == pgid:
                if self._process[pid]["PPID"] == 1:
                    if pid != pgid:
                        pids.append(pid)
        return pids

    def getPids(self):
        """
        Return list of process IDs.
        """
        return sorted(self._process.keys())

    def getProcess(self, pid):
        """
        Return process dictionary.
        """
        return self._process[pid]

    def _getkill(self):
        if "kill" not in _cache.keys():
            if _cache["osname"] == "windows":
                _cache["kill"] = Command("taskkill", flags=["/f"])
            else:
                _cache["kill"] = Command("kill", flags=["-KILL"])
        return _cache["kill"]

    def _getps(self):
        if "ps" not in _cache.keys():
            osname = _cache["osname"]
            if osname == "windows":
                _cache["ps"] = Command("tasklist", flags=["/v"])
            else:
                _cache["ps"] = Command("ps", flags=[
                    "-o", "ruser pid ppid pgid pri nice tty vsz time etime args", "-e"])
                if osname == "linux":
                    if "COLUMNS" not in os.environ.keys():
                        os.environ["COLUMNS"] = "1024"       # Fix Linux ps width
        return _cache["ps"]


class Main:
    """
    This class is the main program.
    """

    def __init__(self):
        self._signals()
        try:
            if "_SYSTEM_BG" in os.environ.keys():
                Background()
            elif "_SYSTEM_DM" in os.environ.keys():
                Daemon()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


# Caching dictionary for this module
_cache = {}
info = SystemInfo()

if __name__ == "__main__":
    if len(sys.argv) == 1 or "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
