#!/usr/bin/env python3
"""
Reset to default screen resolution.

"$HOME/.config/xreset.json" contain configuration information.
"""

import argparse
import json
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Batch


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_settings(self) -> dict:
        """
        Return settings
        """
        return self._config.get()

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Reset to default screen resolution.",
        )

        parser.add_argument(
            'settings',
            nargs='*',
            metavar='device=mode',
            help='Display device (ie "DP1=1920x1080").'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if 'HOME' not in os.environ:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot determine home directory.",
            )

        configdir = Path(Path.home(), '.config')
        if not configdir.is_dir():
            try:
                configdir.mkdir()
            except OSError:
                return
        path = Path(configdir, 'xreset.json')
        self._config = Configuration(path)

        if self._args.settings:
            for setting in self._args.settings:
                try:
                    device, mode = setting.split('=')
                except ValueError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Invalid "{setting}" settings.',
                    ) from exception
                self._config.set(device, mode)
            self._config.write(path)


class Configuration:
    """
    Configuration class
    """

    def __init__(self, path: Path = None) -> None:
        self._data: dict = {'xreset': {}}
        if path:
            try:
                self._data = json.loads(path.read_text(errors='replace'))
            except (OSError, KeyError, ValueError):
                pass

    def get(self) -> dict:
        """
        Return device mode
        """
        return self._data['xreset'].items()

    def set(self, device: str, mode: str) -> None:
        """
        Set device mode
        """
        self._data['xreset'][device] = mode

    def write(self, path: Path) -> None:
        """
        Write file
        """
        try:
            with path.open('w') as ofile:
                print(
                    json.dumps(self._data, indent=4, sort_keys=True),
                    file=ofile
                )
        except OSError:
            pass


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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        xrandr = Command('xrandr', errors='stop')
        dpi = '96'
        settings = options.get_settings()

        Batch(xrandr.get_cmdline() + ['-s', '0']).run()
        Batch(xrandr.get_cmdline() + ['--dpi', dpi]).run()

        for device, mode in settings:
            Batch(xrandr.get_cmdline() + ['--output', device, '--auto']).run()
            Batch(
                xrandr.get_cmdline() + ['--output', device, '--mode', mode]
            ).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
