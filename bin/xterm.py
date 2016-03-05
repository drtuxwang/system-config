#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE/Invisible terminal session

Use '-i' for invisible terminal
"""

import glob
import os
import signal
import sys

import desktop_mod
import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')

FG_COLOUR = '#000000'
BG_COLOUR = '#ffffdd'


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_columns(self):
        """
        Return number of columns.
        """
        return self._columns

    def get_hosts(self):
        """
        Return list of hosts.
        """
        return self._hosts

    def get_terminal(self):
        """
        Return terminal Command class object.
        """
        return self._terminal

    def parse(self, args):
        """
        Parse arguments
        """
        self._columns = '100'
        invis_flag = False

        while len(args) > 1:
            if not args[1].startswith('-'):
                break
            elif args[1] == '-i':
                self._invis_flag = True
            else:
                xterm = syslib.Command('xterm', args=args[1:])
                xterm.run(mode='exec')
            args = args[1:]

        if invis_flag:
            desktop = 'invisible'
        else:
            desktop = desktop_mod.Desktop().detect()
        mapping = {'invisible': XtermInvisible, 'gnome': GnomeTerminal, 'kde': Konsole,
                   'xfce': XfceTerminal, 'Unknown': Xterm}
        self._terminal = mapping[desktop](self)

        if len(args) == 1:
            self._hosts = [syslib.info.get_hostname()]
        else:
            self._hosts = args[1:]


class Xterm(object):
    """
    Xterm class
    """

    def __init__(self, options):
        self._options = options
        self._pattern = '^$'
        self._myhost = syslib.info.get_hostname()
        self._config()

    def _config(self):
        self._command = syslib.Command('xterm')
        self._command.set_args(['-h'])
        self._command.run(mode='batch')
        self._command.set_flags(
            ['-s', '-j', '-sb', '-sl', '4096', '-cc', '33:48,35-38:48,40-58:48,63-255:48', '-fn',
             '-misc-fixed-bold-r-normal--18-*-iso8859-1', '-fg', BG_COLOUR, '-bg', BG_COLOUR,
             '-cr', '#ff0000', '-ls', '-ut', '-geometry', self._options.get_columns() + 'x24'])
        if self._command.is_match_output(' -rightbar '):
            self._command.append_flag('-rightbar')
        self._pattern = '^$'

    @staticmethod
    def get_label_flags(host):
        """
        Return list of flags for setting terminal label
        """
        return ['-T', host.split('@')[-1] + ':']

    @staticmethod
    def get_run_flag():
        """
        Return flag to prefix command
        """
        return '-e'

    @staticmethod
    def _ssh():
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
                except OSError:
                    return
            try:
                os.chmod(sshconfig, int('600', 8))
            except OSError:
                return

    def run(self):
        """
        Start terminal
        """
        ssh = None
        for host in self._options.get_hosts():
            if host == self._myhost:
                self._command.set_args(self.get_label_flags(host))
                self._command.run(mode='background', filter=self._pattern)
            else:
                self._command.set_args(self.get_label_flags(host) + [self.get_run_flag()])
                if not ssh:
                    ssh = syslib.Command('ssh')
                    ssh.set_flags(
                        ['-X', '-o', 'ServerAliveInterval=300', '-o', 'ServerAliveCountMax=3'])
                    self._ssh()
                ssh.set_wrapper(self._command)
                ssh.set_args([host])
                ssh.run(mode='background', filter=self._pattern)


class XtermInvisible(Xterm):
    """
    Xterm (invisible) class
    """

    def run(self):
        ssh = None
        for host in self._options.get_hosts():
            if host == self._myhost:
                self._command.set_args(self.get_label_flags(host))
                self._command.run(mode='background', filter=self._pattern)
            else:
                self._command.set_args(self.get_label_flags(host))
                if not ssh:
                    ssh = syslib.Command('ssh')
                    ssh.set_flags(
                        ['-X', '-o', 'ServerAliveInterval=300', '-o', 'ServerAliveCountMax=3'])
                    self._ssh()
                ssh.set_args([host, 'xterm'])
                for arg in self._command.get_flags() + self._command.get_args():
                    if '#' in arg:
                        ssh.append_arg('"' + arg + '"')
                    else:
                        ssh.append_arg(arg)
                ssh.run(mode='background', filter=self._pattern)


class GnomeTerminal(Xterm):
    """
    Gnome terminal class
    """

    def _config(self):
        self._command = syslib.Command('gnome-terminal')
        self._command.set_flags(['--geometry=' + self._options.get_columns() + 'x24'])
        self._pattern = '^$|: Gtk-WARNING'

    def get_label_flags(self, host):
        """
        Return list of flags for setting terminal label
        """
        return ['--title=' + host.split('@')[-1] + ':']

    def get_run_flag(self):
        """
        Return flag to prefix command
        """
        return '-x'


class Konsole(GnomeTerminal):
    """
    Konsole class
    """

    def _config(self):
        self._command = syslib.Command('konsole')
        self._command.set_flags(['--geometry=' + self._options.get_columns() + 'x24'])

    def get_run_flag(self):
        """
        Return flag to prefix command
        """
        return '-e'


class XfceTerminal(GnomeTerminal):
    """
    Xfce terminal class
    """

    def _config(self):
        self._command = syslib.Command('xfce4-terminal')
        self._command.set_flags(['--geometry=' + self._options.get_columns() + 'x24'])

    def get_label_flags(self, host):
        return ['--title=']  # Must use empty to allow bash/tcsh title changing


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

        options.get_terminal().run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
