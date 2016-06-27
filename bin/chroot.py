#!/usr/bin/env python3
"""
Wrapper for 'chroot' command
"""

import getpass
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_directory(self):
        """
        Return directory.
        """
        return self._directory

    def parse(self, args):
        """
        Parse arguments
        """
        if len(args) != 2 or not os.path.isdir(args[1]):
            chroot = command_mod.Command('chroot', args=args[1:], errors='stop')
            subtask_mod.Exec(chroot.get_cmdline()).run()
        elif getpass.getuser() != 'root':
            sudo = command_mod.Command(
                'sudo', args=['python3', __file__, os.path.abspath(args[1])], errors='stop')
            subtask_mod.Exec(sudo.get_cmdline()).run()
        if not os.path.isfile(os.path.join(args[1], 'bin', 'bash')):
            raise SystemExit(sys.argv[0] + ': Cannot find "/bin/bash" in chroot directory.')
        self._directory = os.path.abspath(args[1])


class Chroot(object):
    """
    Change root class
    """

    def __init__(self, directory):
        self._chroot = command_mod.Command('/usr/sbin/chroot', errors='stop')
        self._chroot.set_args([directory, '/bin/bash', '-l'])
        self._directory = directory
        self._mount = command_mod.Command('mount', errors='stop')

        self._mountpoints = []
        self.mount_dir('-o', 'bind', '/dev', os.path.join(self._directory, 'dev'))
        self.mount_dir('-o', 'bind', '/proc', os.path.join(self._directory, 'proc'))
        if os.path.isdir('/shared') and os.path.isdir(os.path.join(self._directory, 'shared')):
            self.mount_dir('-o', 'bind', '/shared', os.path.join(self._directory, 'shared'))
        self.mount_dir('-t', 'tmpfs', '-o', 'size=256m,noatime,nosuid,nodev', 'tmpfs',
                       os.path.join(self._directory, 'tmp'))
        if (os.path.isdir('/var/run/dbus') and
                os.path.isdir(os.path.join(self._directory, 'var/run/dbus'))):
            self.mount_dir('-o', 'bind', '/var/run/dbus',
                           os.path.join(self._directory, 'var/run/dbus'))

    def mount_dir(self, *args):
        """
        Mount directory
        """
        self._mount.set_args(list(args))
        subtask_mod.Task(self._mount.get_cmdline()).run()
        self._mountpoints.append(args[-1])

    def run(self):
        """
        Start session
        """
        print('Chroot "' + self._directory + '" starting...')
        subtask_mod.Task(self._chroot.get_cmdline()).run()
        umount = command_mod.Command('umount', args=['-l'] + self._mountpoints, errors='stop')
        subtask_mod.Task(umount.get_cmdline()).run()
        print('Chroot "' + self._directory + '" finished!')


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
    def run():
        """
        Start program
        """
        options = Options()

        Chroot(options.get_directory()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
