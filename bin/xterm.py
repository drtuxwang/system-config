#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE/Invisible terminal session

Use '-i' for invisible terminal
"""

import glob
import os
import re
import shutil
import signal
import socket
import sys

import command_mod
import desktop_mod
import subtask_mod

TEXT_FONT = '*-fixed-bold-*-18-*-iso10646-*'
FG_COLOUR = '#009900'
BG_COLOUR = '#000000'


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._config()
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

    @staticmethod
    def _config():
        if "TMUX" in os.environ:
            del os.environ['TMUX']

    def parse(self, args):
        """
        Parse arguments
        """
        self._columns = '100'
        invis_flag = False

        while len(args) > 1:
            if not args[1].startswith('-'):
                break
            if args[1] == '-i':
                invis_flag = True
            else:
                xterm = command_mod.Command(
                    'xterm',
                    args=args[1:],
                    errors='stop'
                )
                subtask_mod.Exec(xterm.get_cmdline()).run()
            args = args[1:]

        terminals = {
            'cinnamon': GnomeTerminal,
            'gnome': GnomeTerminal,
            'kde': Konsole,
            'mate': MateTerminal,
            'xfce': XfceTerminal,
        }
        if invis_flag:
            desktop = 'invisible'
        else:
            desktop = desktop_mod.Desktop.detect()
        self._terminal = terminals.get(desktop, Xterm)(self)

        if len(args) == 1:
            self._hosts = [socket.gethostname().split('.')[0].lower()]
        else:
            self._hosts = args[1:]


class Terminal:
    """
    Terminal class
    """

    def __init__(self, options):
        self._options = options
        self._pattern = '^$'
        self._myhost = socket.gethostname().split('.')[0].lower()
        self._config()

    def _config(self):
        self._command = None

    @staticmethod
    def get_label_flags(host):
        """
        Return list of flags for setting terminal label
        """
        raise NotImplementedError

    @staticmethod
    def get_run_flag():
        """
        Return flag to prefix command
        """
        raise NotImplementedError

    @staticmethod
    def run():
        """
        Start terminal
        """
        raise NotImplementedError


class Iterm(Terminal):
    """
    Iterm class
    """

    def _config(self):
        self._command = command_mod.Command('iterm', errors='stop')

    @staticmethod
    def get_label_flags(host):
        """
        Return list of flags for setting terminal label
        """
        raise NotImplementedError

    @staticmethod
    def get_run_flag():
        """
        Return flag to prefix command
        """
        raise NotImplementedError

    def run(self):
        """
        Start terminal
        """
        for _ in self._options.get_hosts():
            cmdline = self._command.get_cmdline()
            subtask_mod.Background(cmdline).run(pattern=self._pattern)


class Xterm(Terminal):
    """
    Xterm class
    """

    def _config(self):
        self._command = command_mod.Command('xterm', errors='stop')
        task = subtask_mod.Batch(self._command.get_cmdline() + ['-h'])
        task.run()
        self._command.set_args([
            '-s',
            '-j',
            '-sb',
            '-sl',
            '4096',
            '-cc',
            '33:48,35-38:48,40-58:48,63-255:48',
            '-fn',
            TEXT_FONT,
            '-fg',
            FG_COLOUR,
            '-bg',
            BG_COLOUR,
            '-cr',
            '#ff0000',
            '-ls',
            '-ut',
            '-geometry',
            self._options.get_columns() + 'x24'
        ])
        if task.is_match_output(' -rightbar '):
            self._command.append_arg('-rightbar')
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
        home = os.environ.get('HOME', '')
        sshdir = os.path.join(home, '.ssh')
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
                    print("Protocol 2\n", file=ofile)
                    print("#Host hostname", file=ofile)
                    print("#User username\n", file=ofile)
            except OSError:
                return
        try:
            os.chmod(sshconfig, int('600', 8))
        except OSError:
            return

    @staticmethod
    def _check_server(host):
        try:
            socket.gethostbyname(host)
        except socket.gaierror as exception:
            raise SystemExit("{0:s}: Could not resolve: {1:s}".format(
                sys.argv[0],
                host,
            )) from exception

    def run(self):
        """
        Start terminal
        """
        ssh = None
        for host in self._options.get_hosts():
            cmdline = self._command.get_cmdline() + self.get_label_flags(host)
            if host != self._myhost:
                self._check_server(host)
                cmdline.append(self.get_run_flag())
                if not ssh:
                    ssh = command_mod.Command('ssh', errors='stop')
                    ssh.set_args([
                        '-X',
                        '-o',
                        'ServerAliveInterval=300',
                        '-o',
                        'ServerAliveCountMax=3'
                    ])
                    self._ssh()
                cmdline.extend(ssh.get_cmdline() + [host])
            subtask_mod.Background(cmdline).run(pattern=self._pattern)


class XtermInvisible(Xterm):
    """
    Xterm (invisible) class
    """

    def run(self):
        ssh = None
        for host in self._options.get_hosts():
            if host == self._myhost:
                task = subtask_mod.Background(
                    self._command.get_cmdline() + self.get_label_flags(host))
                task.run(pattern=self._pattern)
            else:
                if not ssh:
                    ssh = command_mod.Command('ssh', errors='stop')
                    ssh.set_args([
                        '-X',
                        '-o',
                        'ServerAliveInterval=300',
                        '-o',
                        'ServerAliveCountMax=3'
                    ])
                    self._ssh()
                ssh.set_args([host, 'xterm'])
                for arg in (
                        self._command.get_cmdline() +
                        self.get_label_flags(host) + self._command.get_args()
                ):
                    if '#' in arg:
                        ssh.append_arg('"' + arg + '"')
                    else:
                        ssh.append_arg(arg)
                subtask_mod.Background(
                    ssh.get_cmdline()).run(pattern=self._pattern)


class GnomeTerminal(Xterm):
    """
    Gnome terminal class
    """

    def _config(self):
        self._command = command_mod.Command('gnome-terminal', errors='stop')
        self._command.set_args(
            ['--geometry=' + self._options.get_columns() + 'x24'])
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
        self._command = command_mod.Command('konsole', errors='stop')
        self._command.set_args(
            ['--geometry=' + self._options.get_columns() + 'x24']
        )

    def get_run_flag(self):
        """
        Return flag to prefix command
        """
        return '-e'


class MateTerminal(Konsole):
    """
    MateTerminal class
    """

    def _config(self):
        self._command = command_mod.Command('mate-terminal', errors='stop')
        self._command.set_args(
            ['--geometry=' + self._options.get_columns() + 'x24']
        )


class XfceTerminal(GnomeTerminal):
    """
    Xfce terminal class (fallback to gnome-terminal)
    """

    def __init__(self, options):
        super().__init__(options)
        self._pattern = (
            '^$|: Gtk-WARNING|: Failed to connect to |'
            ': GLib-WARNING |: SESSION_MANAGER'
        )

    def _config(self):
        file = os.path.join(
            os.environ.get('HOME', ''),
            '.config/xfce4/terminal/accels.scm',
        )
        try:
            with open(file, errors='replace') as ifile:
                data = ifile.read()
                if '"<Alt>' in data:
                    with open(file+'.part', 'w', newline='\n') as ofile:
                        print(re.sub(r'"<Alt>\d+"', '""', data), file=ofile)
                    shutil.move(file+'.part', file)
        except OSError:
            return

        self._command = command_mod.Command(
            'xfce4-terminal',
            errors='ignore'
        )
        if not self._command.is_found():
            self._command = command_mod.Command(
                'gnome-terminal',
                errors='ignore'
            )
            if not self._command.is_found():
                self._command = command_mod.Command(
                    'xfce4-terminal',
                    errors='stop'
                )

        self._command.set_args(
            ['--geometry=' + self._options.get_columns() + 'x24'])

    def get_label_flags(self, host):
        return ['--title=']  # Must use empty to allow bash/tcsh title changing


class Main:
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
