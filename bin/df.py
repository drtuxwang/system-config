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

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class CommandThread(threading.Thread):
    """
    Command thread class
    """

    def __init__(self, command):
        threading.Thread.__init__(self, daemon=True)
        self._child = None
        self._command = command
        self._stdout = ''

    def get_output(self):
        """
        Return thread output.
        """
        return self._stdout

    def run(self):
        """
        Start thread
        """
        self._child = subtask_mod.Child(self._command.get_cmdline()).run()
        while True:
            try:
                byte = self._child.stdout.read(1)
            except AttributeError:
                continue
            if not byte:
                break
            self._stdout += byte.decode('utf-8', 'replace')

    def kill(self):
        """
        Terminate thread
        """
        if self._child:
            self._child.kill()
            self._child = None


class Main(object):
    """
    Main class
    """

    def __init__(self):
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def _detect():
        mount = command_mod.Command('mount', errors='stop')
        task = subtask_mod.Batch(mount.get_cmdline())
        task.run()

        mounts = []
        for line in task.get_output():
            try:
                directory, info = line.split(' ', 3)[2:]
            except IndexError:
                continue
            if 'none' not in info:
                mounts.append(directory)

        return mounts

    def _show(self):
        devices = {}
        for file in glob.glob('/dev/disk/by-uuid/*'):
            try:
                devices[file] = '/dev/' + os.path.basename(os.readlink(file))
            except OSError:
                pass

        print('Filesystem       1K-blocks       Used  Available Use% Mounted on')
        for mount in self._mounts:
            self._command.set_args([mount])
            thread = CommandThread(self._command)
            thread.start()
            end_time = time.time() + 1  # One second delay limit
            while thread.is_alive():
                if time.time() > end_time:
                    thread.kill()
                    break
            try:
                device, blocks, used, avail, ratio, directory = thread.get_output().split()[-6:]
                if int(blocks) != 0:
                    if device in devices:  # Map UUID to device
                        device = devices[device]
                    if len(device) > 15:
                        print(device)
                        device = ''
                    print('{0:15s} {1:>10s} {2:>10s} {3:>10s} {4:>4s} {5:s}'.format(
                        device, blocks, used, avail, ratio, directory))
            except (IndexError, ValueError):
                continue

    def run(self):
        """
        Generate report
        """
        self._command = command_mod.Command(
            'df', args=sys.argv[1:], pathextra=['/bin'], errors='stop')

        if command_mod.Platform.get_system() == 'macos':
            subtask_mod.Exec(self._command.get_cmdline() + sys.argv[1:]).run()

        args = sys.argv
        while len(args) > 1:
            if not args[1].startswith('-'):
                break
            elif args[1] != '-k':
                subtask_mod.Exec(self._command.get_cmdline()).run()
            args = args[1:]

        self._mounts = args[1:]
        if not self._mounts:
            self._mounts = self._detect()

        self._show()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
