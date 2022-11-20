#!/usr/bin/env python3
"""
VirtualBox virtual machine manager.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_mode(self) -> str:
        """
        Return operation mode.
        """
        return self._args.mode

    def get_machines(self) -> List[str]:
        """
        Return list of virtual machines.
        """
        return self._args.machines

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="VirtualBox virtual machine manager.",
        )

        parser.add_argument(
            '-p',
            action='store_const',
            const='poweroff',
            dest='mode',
            default='start',
            help="Power off virtual machine.",
        )
        parser.add_argument(
            '-s',
            action='store_const',
            const='shutdown',
            dest='mode',
            default='start',
            help="Shutdown virtual machine.",
        )
        parser.add_argument(
            '-v',
            action='store_const',
            const='view',
            dest='mode',
            default='start',
            help="List virtual machine.",
        )
        parser.add_argument(
            'machines',
            nargs='+',
            metavar='machine',
            help="Virtual machine.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _poweroff(self, machines: List[str]) -> None:
        for machine in machines:
            self._vboxmanage.set_args(['controlvm', machine, 'poweroff'])
            task = subtask_mod.Task(self._vboxmanage.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

    def _shutdown(self, machines: List[str]) -> None:
        for machine in machines:
            self._vboxmanage.set_args(
                ['controlvm', machine, 'acpipowerbutton'])
            task = subtask_mod.Task(self._vboxmanage.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

    def _start(self, machines: List[str]) -> None:
        for machine in machines:
            self._vboxmanage.set_args(
                ['startvm', machine, '--type', 'headless'])
            task = subtask_mod.Task(self._vboxmanage.get_cmdline())
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

    def _view(self) -> None:
        self._vboxmanage.set_args(['list', 'vms'])
        task = subtask_mod.Task(self._vboxmanage.get_cmdline())
        task.run(pattern='^".*"')
        if task.has_output():
            lines = sorted(task.get_output())
            self._vboxmanage.set_args(['list', 'runningvms'])
            task = subtask_mod.Task(self._vboxmanage.get_cmdline())
            task.run(pattern='^".*"')
            for line in lines:
                if line in task.get_output():
                    print("[Run]", line)
                else:
                    print("[Off]", line)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._vboxmanage = command_mod.Command('VBoxManage', errors='stop')
        mode = options.get_mode()
        machines = options.get_machines()

        if mode == 'view':
            self._view()
        elif mode == 'poweroff':
            self._poweroff(machines)
        elif mode == 'shutdown':
            self._shutdown(machines)
        else:
            self._start(machines)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
