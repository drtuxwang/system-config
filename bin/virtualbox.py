#!/usr/bin/env python3
"""
Wrapper for "virtualbox" command
"""

import os
import signal
import sys
from pathlib import Path

import command_mod
import config_mod
import subtask_mod


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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _config_machine(machine: dict) -> None:
        vboxmanage = command_mod.Command('vboxmanage')
        name = machine['@name']

        try:
            controllers = (
                machine['Hardware']['StorageControllers']['StorageController']
            )
        except KeyError:
            return
        if not isinstance(controllers, list):
            controllers = [controllers]
        for controller in controllers:
            for device in controller.get('AttachedDevice', []):
                try:
                    if device.get('@type') == 'HardDisk' and (
                        device.get('@nonrotational') != 'true' or
                        device.get('@discard') != 'true'
                    ):
                        vboxmanage.set_args([
                            'storageattach',
                            name,
                            f"--storagectl={controller['@name']}",
                            f"--port={device['@port']}",
                            f"--device={device['@device']}",
                            '--type=hdd',
                            '--nonrotational=on',
                            '--discard=on',
                            f"--medium={device['Image']['@uuid']}",
                        ])
                        print(vboxmanage.args2cmd(vboxmanage.get_cmdline()))
                        subtask_mod.Task(vboxmanage.get_cmdline()).run()
                except KeyError:
                    pass

    @classmethod
    def _config(cls) -> None:
        data = config_mod.Data()
        path = Path(Path.home(), '.config', 'VirtualBox', 'VirtualBox.xml')
        try:
            data.read(path)
        except config_mod.ReadConfigError:
            return
        try:
            for file in [x['@src'] for x in next(data.get())[
                'VirtualBox'
            ]['Global']['MachineRegistry']['MachineEntry']]:
                data.read(file, config='XML')
                cls._config_machine(next(data.get())['VirtualBox']['Machine'])
        except KeyError:
            pass

    @classmethod
    def run(cls) -> None:
        """
        Start program
        """
        command = command_mod.Command('virtualbox', errors='stop')
        command.set_args(sys.argv[1:])
        cls._config()

        pattern = "^$|: dbind-WARNING"
        subtask_mod.Background(command.get_cmdline()).run(pattern=pattern)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
