#!/usr/bin/env python3
"""
Set CD/DVD drive speed.

"$HOME/.config/cdspeed.json" contain configuration information.
"""

import argparse
import glob
import json
import os
import shutil
import signal
import socket
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

        configdir = os.path.join(os.environ.get('HOME', ''), '.config')
        if not os.path.isdir(configdir):
            try:
                os.mkdir(configdir)
            except OSError:
                return None
        configfile = os.path.join(configdir, 'cdspeed.json')
        if os.path.isfile(configfile):
            config = Configuration(configfile)
            old_speed = config.get_speed(self._device)
            if old_speed:
                if speed == 0:
                    speed = old_speed
                elif speed == old_speed:
                    return speed
        else:
            config = Configuration()
        config.set_speed(self._device, speed)
        config.write(configfile + '.part')
        try:
            shutil.move(configfile + '.part', configfile)
        except OSError:
            os.remove(configfile + '.part')

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
            '/sbin/hdparm', args=['-E', str(self._speed), self._device])
        print("Setting CD/DVD drive speed to ", self._speed, "X", sep="")


class Configuration:
    """
    Configuration class
    """

    def __init__(self, file: str = '') -> None:
        self._data: dict = {'cdspeed': {}}
        if file:
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
                    self._data = json.load(ifile)
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

    def write(self, file: str) -> None:
        """
        Write file
        """
        try:
            with open(file, 'w', encoding='utf-8', newline='\n') as ofile:
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
