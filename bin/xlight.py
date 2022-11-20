#!/usr/bin/env python3
"""
Desktop screen backlight utility.
"""

import argparse
import getpass
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

    def get_change(self) -> float:
        """
        Return change.
        """
        return self._args.change

    def get_backlight(self) -> 'Backlight':
        """
        Return BacklightXXX class object.
        """
        return self._backlight

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Desktop screen backlight utility.",
        )

        parser.add_argument(
            '-dec',
            action='store_const',
            const='-', dest='change',
            help="Increase brightness.",
        )
        parser.add_argument(
            '-inc',
            action='store_const',
            const='+',
            dest='change',
            help="Default brightness.",
        )
        parser.add_argument(
            '-reset',
            action='store_const',
            const='=',
            dest='change',
            help="Decrease brightness.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        if args[1:2] == ['setpci']:
            setpci = command_mod.Command('setpci', errors='stop')
            subtask_mod.Exec(setpci.get_cmdline() + args[2:]).run()

        self._parse_args(args[1:])
        self._backlight = Backlight.factory()


class Backlight:
    """
    Backlight base class
    """

    def __init__(self) -> None:
        self._device = self._get_device()
        self._max = self.get_brightness_max()
        self._default = self.get_brightness_default()
        self._step = self.get_brightness_step()

        self._command: command_mod.Command = None
        self._screens: List[str] = None

    @staticmethod
    def factory() -> 'Backlight':
        """
        Return Backlight sub class object
        """
        for backlight in (
                BacklightIntel(), BacklightIntelSetpci(), BacklightXrandr()):
            if backlight.detect():
                return backlight
        raise SystemExit(f"{sys.argv[0]}: Cannot detect backlight device.")

    @staticmethod
    def _get_device() -> str:
        return '/sys/class/backlight/acpi_video0'

    def get_brightness(self) -> float:
        """
        Return brightness
        """
        try:
            with open(
                os.path.join(self._device, 'brightness'),
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                brightness = int(ifile.readline())
        except (OSError, ValueError):
            brightness = 0
        return brightness

    def get_brightness_default(self) -> float:
        """
        Return brightness default
        """
        return int(self._max / 8)

    def get_brightness_max(self) -> float:
        """
        Return brightness max
        """
        try:
            with open(
                os.path.join(self._device, 'max_brightness'),
                encoding='utf-8',
                errors='replace',
            ) as ifile:
                brightness = int(ifile.readline())
        except (OSError, ValueError):
            brightness = 0
        return brightness

    def get_brightness_step(self) -> float:
        """
        Return brightness step size
        """
        return int(self._max / 24)

    def set_brightness(self, brightness: float) -> None:
        """
        set brightness
        """
        try:
            with open(
                os.path.join(self._device, 'brightness'),
                'w',
                encoding='utf-8',
                newline='\n',
            ) as ofile:
                print(brightness, file=ofile)
        except OSError:
            pass

    def detect(self) -> bool:
        """
        Detect status
        """
        file = os.path.join(self._device, 'brightness')
        if os.path.isfile(file):
            if getpass.getuser() != 'root':
                try:
                    os.chmod(file, int('666', 8))
                except OSError:
                    pass
            return True
        return False

    def run(self, change: float) -> None:
        """
        Run change
        """
        if change:
            if change == '+':
                brightness = min(self.get_brightness() + self._step, self._max)
            elif change == '-':
                brightness = max(self.get_brightness()-self._step, 0)
            elif change == '=':
                brightness = self._default
            self.set_brightness(brightness)
        else:
            print(
                f"{self.get_brightness() + 0.01:3.1f} / "
                f"{self._max + 0.01:3.1f}",
            )


class BacklightIntel(Backlight):
    """
    Backlight intel class
    """

    @staticmethod
    def _get_device() -> str:
        return '/sys/class/backlight/intel_backlight'


class BacklightIntelSetpci(Backlight):
    """
    Backlight Intel (setpci) class
    """

    @staticmethod
    def _get_device() -> str:
        return ''

    def get_brightness(self) -> float:
        """
        Return brightness
        """
        if getpass.getuser() != 'root':
            sudo = command_mod.Command('sudo', errors='stop')
            sudo.set_args(['-n', sys.argv[0]])
            task = subtask_mod.Batch(
                sudo.get_cmdline() + self._command.get_cmdline() + ['F4.B']
            )
        else:
            task = subtask_mod.Batch(self._command.get_cmdline() + ['F4.B'])
        task.run()
        try:
            return int(int(task.get_output()[0], 16) / 16)  # From 0 - 15
        except (IndexError, ValueError) as exception:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot detect current brightness setting.",
            ) from exception

    def get_brightness_default(self) -> float:
        """
        Return brightness default
        """
        return 3

    def get_brightness_max(self) -> float:
        """
        Return brightness max
        """
        return 15

    def get_brightness_step(self) -> float:
        """
        Return brightness step size
        """
        return 1

    def set_brightness(self, brightness: float) -> None:
        """
        Set brightness
        """
        self._command.set_args(['F4.B={int(brightness*16 + 15):x}'])
        subtask_mod.Exec(self._command.get_cmdline()).run()

    def detect(self) -> bool:
        """
        Detect status
        """
        lspci = command_mod.Command('lspci', errors='ignore')
        if lspci.is_found():
            task = subtask_mod.Batch(lspci.get_cmdline())
            task.run(pattern='VGA.*Intel.*Atom')
            if task.has_output():
                self._command = command_mod.Command(
                    'setpci',
                    args=['-s', task.get_output()[0].split()[0]],
                    errors='stop'
                )
                return True
        return False


class BacklightXrandr(Backlight):
    """
    Backlight xrandr class
    """

    @staticmethod
    def _get_device() -> str:
        return ''

    def get_brightness(self) -> float:
        """
        Return brightness
        """
        self._command.set_args(['--verbose'])
        task = subtask_mod.Batch(self._command.get_cmdline())
        task.run()
        try:
            brightness = float(
                task.get_output(r'^\s+Brightness: ')[0].split()[1])
        except (IndexError, ValueError):
            brightness = 0.
        return brightness

    def get_brightness_default(self) -> float:
        """
        Return brightness default
        """
        return 0.999

    def get_brightness_max(self) -> float:
        """
        Return brightness max
        """
        return 0.999

    def get_brightness_step(self) -> float:
        """
        Return brightness step size
        """
        return 0.1

    def set_brightness(self, brightness: float) -> None:
        """
        Set brightness
        """
        for screen in self._screens:
            self._command.set_args(
                ['--output', screen, '--brightness', str(brightness)])
            subtask_mod.Task(self._command.get_cmdline()).run()

    def detect(self) -> bool:
        """
        Detect status
        """
        self._command = command_mod.Command('xrandr', errors='ignore')
        if self._command.is_found():
            task = subtask_mod.Batch(self._command.get_cmdline())
            task.run()
            self._screens: List[str] = []
            for line in task.get_output('^[^ ]* connected '):
                self._screens.append(line.split()[0])
            if self._screens:
                return True
        return False


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

        options.get_backlight().run(options.get_change())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
