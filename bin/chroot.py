#!/usr/bin/env python3
"""
Wrapper for 'chroot' command
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        if len(args) != 2 or not os.path.isdir(args[1]):
            chroot = syslib.Command('chroot', args=args[1:])
            chroot.run(mode='exec')
        elif syslib.info.get_username() != 'root':
            sudo = syslib.Command('sudo', args=['python3', __file__ , os.path.abspath(args[1])])
            sudo.run(mode='exec')
        if not os.path.isfile(os.path.join(args[1], 'bin', 'bash')):
            raise SystemExit(sys.argv[0] + ': Cannot find "/bin/bash" in chroot directory.')
        self._directory = os.path.abspath(args[1])

    def get_directory(self):
        """
        Return directory.
        """
        return self._directory


class Chroot(object):
    """
    Change root class
    """

    def __init__(self, directory):
        self._chroot = syslib.Command('/usr/sbin/chroot')
        self._chroot.set_args([directory, '/bin/bash', '-l'])
        self._directory = directory
        self._mount = syslib.Command('mount')
        self._mountpoints = []
        self._mount_dir('-o', 'bind', '/dev', os.path.join(self._directory, 'dev'))
        self._mount_dir('-o', 'bind', '/proc', os.path.join(self._directory, 'proc'))
        if os.path.isdir('/shared') and os.path.isdir(os.path.join(self._directory, 'shared')):
            self._mount_dir('-o', 'bind', '/shared', os.path.join(self._directory, 'shared'))
        self._mount_dir('-t', 'tmpfs', '-o', 'size=256m,noatime,nosuid,nodev', 'tmpfs',
                        os.path.join(self._directory, 'tmp'))
        if (os.path.isdir('/var/run/dbus') and
                os.path.isdir(os.path.join(self._directory, 'var/run/dbus'))):
            self._mount_dir('-o', 'bind', '/var/run/dbus',
                            os.path.join(self._directory, 'var/run/dbus'))

    def _getterm(self):
        term = 'Unkown'
        if 'TERM' in os.environ:
            term = os.environ['TERM']
        return term

    def _mount_dir(self, *args):
        self._mount.set_args(list(args))
        self._mount.run()
        self._mountpoints.append(args[-1])

    def run(self):
        """
        Start session
        """
        print('Chroot "' + self._directory + '" starting...')
        if self._getterm() in ['xterm', 'xvt100']:
            sys.stdout.write(
                '\033]0;' + syslib.info.get_hostname() + ':' + self._directory + '\007')
            sys.stdout.flush()
        self._chroot.run()
        if self._getterm() in ['xterm', 'xvt100']:
            sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':\007')
        syslib.Command('umount', args=['-l'] + self._mountpoints).run()
        print('Chroot "' + self._directory + '" finished!')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Chroot(options.get_directory()).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
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
