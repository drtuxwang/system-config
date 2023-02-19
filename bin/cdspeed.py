#!/usr/bin/env python3
"""
Set CD/DVD drive speed.

"$HOME/.config/cdspeed.json" contain configuration information.
"""

import argparse
import json
import os
import signal
import socket
import sys
from pathlib import Path
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

    def get_hdparm(self) -> command_mod.Command:
        """
        Return hdparm Command class object.
        """
        return self._hdparm

    def _config_speed(self) -> int:
        if self._args.speed:
            speed = self._args.speed
            if speed < 0:
                raise SystemExit(
                    f"{sys.argv[0]}: You must specific a positive integer for "
                    "CD/DVD device speed.",
                )
        else:
            speed = 0

        path = Path(Path.home(), '.config')
        if not path.is_dir():
            try:
                path.mkdir()
            except OSError:
                return None
        path = Path(path, 'cdspeed.json')
        if path.is_file():
            config = Configuration(path)
            old_speed = config.get_speed(self._device)
            if old_speed:
                if speed == 0:
                    speed = old_speed
                elif speed == old_speed:
                    return speed
        else:
            config = Configuration()
        config.set_speed(self._device, speed)

        path_new = Path(f'{path}.part')
        config.write(path_new)
        try:
            path_new.replace(path)
        except OSError:
            os.remove(path_new)

        return speed

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(description="Set CD/DVD drive speed.")

        parser.add_argument(
            'device',
            nargs=1,
            help="CD/DVD device (ie '/dev/sr0')."
        )
        parser.add_argument(
            'speed',
            nargs='?',
            type=int,
            help="Select CD/DVD spin speed.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._device = (
            f"{socket.gethostname().split('.')[0].lower()}:"
            f"{self._args.device[0]}"
        )

        self._speed = self._config_speed()
        if self._speed == 0:
            raise SystemExit(0)

        self._hdparm = command_mod.CommandFile(
            '/sbin/hdparm',
            args=['-E', self._speed, self._device],
        )
        print("Setting CD/DVD drive speed to ", self._speed, "X", sep="")


class Configuration:
    """
    Configuration class
    """

    def __init__(self, path: Path = None) -> None:
        self._data: dict = {'cdspeed': {}}
        if path:
            try:
                self._data = json.loads(path.read_text(errors='replace'))
            except (KeyError, OSError):
                pass

    def get_speed(self, device: str) -> int:
        """
        Get speed
        """
        try:
            return self._data['cdspeed'][device]
        except KeyError:
            return 0

    def set_speed(self, device: str, speed: int) -> None:
        """
        Set speed
        """
        self._data['cdspeed'][device] = speed

    def write(self, path: Path) -> None:
        """
        Write file
        """
        try:
            with path.open('w') as ofile:
                print(json.dumps(
                    self._data,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                ), file=ofile)
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

        subtask_mod.Batch(options.get_hdparm().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
