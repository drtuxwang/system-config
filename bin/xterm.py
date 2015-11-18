#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE/Invisible terminal session

Use '-i' for invisible terminal
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        self._columns = '100'
        self._invisFlag = False

        while len(args) > 1:
            if not args[1].startswith('-'):
                break
            elif args[1] == '-i':
                self._invisFlag = True
            else:
                xterm = syslib.Command('xterm', args=args[1:])
                xterm.run(mode='exec')
            args = args[1:]

        self._desktop = self._getDesktop()
        if self._desktop == 'invisible':
            self._terminal = XtermInvisible(self)
        elif self._desktop == 'gnome':
            self._terminal = GnomeTerminal(self)
        elif self._desktop == 'kde':
            self._terminal = Konsole(self)
        elif self._desktop == 'xfce':
            self._terminal = XfceTerminal(self)
        else:
            self._terminal = Xterm(self)
        if len(args) == 1:
            self._hosts = [syslib.info.getHostname()]
        else:
            self._hosts = args[1:]

    def getColumns(self):
        """
        Return number of columns.
        """
        return self._columns

    def getHosts(self):
        """
        Return list of hosts.
        """
        return self._hosts

    def getTerminal(self):
        """
        Return terminal Command class object.
        """
        return self._terminal

    def _getDesktop(self):
        if self._invisFlag:
            return 'invisible'
        else:
            keys = os.environ.keys()
            if 'XDG_MENU_PREFIX' in keys and os.environ['XDG_MENU_PREFIX'] == 'xfce-':
                return 'xfce'
            if 'XDG_CURRENT_DESKTOP' in keys and os.environ['XDG_CURRENT_DESKTOP'] == 'XFCE':
                return 'xfce'
            if 'XDG_DATA_DIRS' in keys and '/xfce' in os.environ['XDG_DATA_DIRS']:
                return 'xfce'
            if 'DESKTOP_SESSION' in keys:
                if 'gnome' in os.environ['DESKTOP_SESSION']:
                    return 'gnome'
                if 'kde' in os.environ['DESKTOP_SESSION']:
                    return 'kde'
            if 'GNOME_DESKTOP_SESSION_ID' in keys:
                return 'gnome'
        return 'Unknown'


class Xterm:

    def __init__(self, options):
        self._options = options
        self._filter = '^$'
        self._myhost = syslib.info.getHostname()
        self._command()

    def _command(self):
        self._command = syslib.Command('xterm')
        self._command.setArgs(['-h'])
        self._command.run(mode='batch')
        self._command.setFlags(['-s', '-j', '-sb', '-sl', '4096',
                                '-cc', '33:48,35-38:48,40-58:48,63-255:48',
                                '-fn', '-misc-fixed-bold-r-normal--18-*-iso8859-1',
                                '-fg', '#000000', '-bg', '#ffffdd', '-cr', '#ff00ff',
                                '-ls', '-ut', '-geometry', self._options.getColumns() + 'x24'])
        if self._command.isMatchOutput(' -rightbar '):
            self._command.appendFlag('-rightbar')
        self._filter = '^$'

    def _getlabelFlags(self, host):
        return ['-T', host.split('@')[-1] + ':']

    def _getrunFlag(self):
        return '-e'

    def _ssh(self):
        if 'HOME' in os.environ:
            sshdir = os.path.join(os.environ['HOME'], '.ssh')
            if not os.path.isdir(sshdir):
                try:
                    os.mkdir(sshdir)
                except OSError:
                    return
            os.chmod(sshdir, int('700', 8))
            sshconfig = os.path.join(sshdir, 'config')
            if not os.path.isfile(sshconfig):
                try:
                    with open(sshconfig, 'w', newline='\n') as ofile:
                        print('Protocol 2\n', file=ofile)
                        print('#Host hostname', file=ofile)
                        print('#User username\n', file=ofile)
                except IOError:
                    return
            try:
                os.chmod(sshconfig, int('600', 8))
            except OSError:
                return

    def run(self):
        ssh = None
        for host in self._options.getHosts():
            if host == self._myhost:
                self._command.setArgs(self._getlabelFlags(host))
                self._command.run(mode='background', filter=self._filter)
            else:
                self._command.setArgs(self._getlabelFlags(host) + [self._getrunFlag()])
                if not ssh:
                    ssh = syslib.Command('ssh')
                    ssh.setFlags(['-X', '-o', 'ServerAliveInterval=300',
                                  '-o', 'ServerAliveCountMax=3'])
                    self._ssh()
                ssh.setWrapper(self._command)
                ssh.setArgs([host])
                ssh.run(mode='background', filter=self._filter)


class XtermInvisible(Xterm):

    def run(self):
        ssh = None
        for host in self._options.getHosts():
            if host == self._myhost:
                self._command.setArgs(self._getlabelFlags(host))
                self._command.run(mode='background', filter=self._filter)
            else:
                self._command.setArgs(self._getlabelFlags(host))
                if not ssh:
                    ssh = syslib.Command('ssh')
                    ssh.setFlags(['-X', '-o', 'ServerAliveInterval=300',
                                  '-o', 'ServerAliveCountMax=3'])
                    self._ssh()
                ssh.setArgs([host, 'xterm'])
                for arg in self._command.getFlags() + self._command.getArgs():
                    if '#' in arg:
                        ssh.appendArg('"' + arg + '"')
                    else:
                        ssh.appendArg(arg)
                ssh.run(mode='background', filter=self._filter)


class GnomeTerminal(Xterm):

    def _command(self):
        self._command = syslib.Command('gnome-terminal')
        self._command.setFlags(['--geometry=' + self._options.getColumns() + 'x24'])
        self._filter = '^$|: Gtk-WARNING'

    def _getlabelFlags(self, host):
        return ['--title=' + host.split('@')[-1] + ':']

    def _getrunFlag(self):
        return '-x'


class Konsole(GnomeTerminal):

    def _command(self):
        self._command = syslib.Command('konsole')
        self._command.setFlags(['--geometry=' + self._options.getColumns() + 'x24'])

    def _getrunFlag(self):
        return '-e'


class XfceTerminal(GnomeTerminal):

    def _command(self):
        self._command = syslib.Command('xfce4-terminal')
        self._command.setFlags(['--geometry=' + self._options.getColumns() + 'x24'])

    def _getlabelFlags(self, host):
        return ['--title=']  # Must use empty to allow bash/tcsh title changing


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getTerminal().run()
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
