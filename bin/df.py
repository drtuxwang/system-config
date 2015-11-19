#!/usr/bin/env python3
"""
Wrapper for 'df' command
"""

import glob
import os
import signal
import sys
import threading
import time

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options:

    def __init__(self, args):
        self._df = syslib.Command('df', args=args[1:], pathextra=['/bin'])

        while len(args) > 1:
            if not args[1].startswith('-'):
                break
            elif args[1] != '-k':
                self._df.run(mode='exec')
            args = args[1:]

        self._mounts = args[1:]

    def getDf(self):
        """
        Return df Command class object.
        """
        return self._df

    def getMounts(self):
        """
        Return list of disk mounts.
        """
        return self._mounts


class CommandThread(threading.Thread):

    def __init__(self, command):
        threading.Thread.__init__(self)
        self._child = None
        self._command = command
        self._stdout = ''

    def run(self):
        self._child = self._command.run(mode='child')
        while True:
            try:
                byte = self._child.stdout.read(1)
            except AttributeError:
                continue
            if not byte:
                break
            self._stdout += byte.decode('utf-8', 'replace')

    def kill(self):
        if self._child:
            self._child.kill()
            self._child = None

    def getOutput(self):
        """
        Return thread output.
        """
        return self._stdout


class DiskReport:

    def __init__(self, options):
        self._df = options.getDf()
        self._mounts = options.getMounts()
        if not self._mounts:
            self._detect()

    def run(self):
        devices = {}
        for file in glob.glob('/dev/disk/by-uuid/*'):
            try:
                devices[file] = '/dev/' + os.path.basename(os.readlink(file))
            except OSError:
                pass

        print('Filesystem       1K-blocks       Used  Available Use% Mounted on')
        for mount in self._mounts:
            self._df.setArgs([mount])
            thread = CommandThread(self._df)
            thread.start()
            endTime = time.time() + 1  # One second delay limit
            while thread.is_alive():
                if time.time() > endTime:
                    thread.kill()
                    break
            try:
                device, blocks, used, avail, ratio, directory = thread._stdout.split()[-6:]
            except (IndexError, ValueError):
                continue

            if blocks != '0':
                if device in devices:  # Map UUID to device
                    device = devices[device]
                if len(device) > 15:
                    print(device)
                    device = ''
                print('{0:15s} {1:>10s} {2:>10s} {3:>10s} {4:>4s} {5:s}'.
                      format(device, blocks, used, avail, ratio, directory))

    def _detect(self):
        mount = syslib.Command('mount')
        mount.run(mode='batch')
        for line in mount.getOutput():
            try:
                device, junk, directory, info = line.split(' ', 3)
            except IndexError:
                continue
            if 'none' not in info:
                self._mounts.append(directory)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            DiskReport(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
