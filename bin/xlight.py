#!/usr/bin/env python3
"""
Desktop screen backlight utility.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._backlight = self._get_backlight()

    def get_change(self):
        """
        Return change.
        """
        return self._args.change

    def get_backlight(self):
        """
        Return BacklightXXX class object.
        """
        return self._backlight

    def _get_backlight(self):
        for backlight in (BacklightIntel(), BacklightIntelSetpci(), BacklightXrandr()):
            if backlight.detect():
                return backlight
        raise SystemExit(sys.argv[0] + ": Cannot detect backlight device.")

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Desktop screen backlight utility.')

        parser.add_argument('-dec', action='store_const', const='-', dest='change',
                            help='Increase brightness.')
        parser.add_argument('-inc', action='store_const', const='+', dest='change',
                            help='Default brightness.')
        parser.add_argument('-reset', action='store_const', const='=', dest='change',
                            help='Decrease brightness.')

        self._args = parser.parse_args(args)


class Backlight(object):
    """
    Backlight class
    """

    def __init__(self):
        self._device = self._get_device()
        self._max = self.get_brightness_max()
        self._default = self.get_brightness_default()
        self._step = self.get_brightness_step()

    def detect(self):
        file = os.path.join(self._device, 'brightness')
        if os.path.isfile(file):
            if syslib.info.get_username() != 'root':
                try:
                    os.chmod(file, int('666', 8))
                except OSError:
                    pass
            return True
        return False

    def _get_device(self):
        return '/sys/class/backlight/acpi_video0'

    def get_brightness(self):
        try:
            with open(os.path.join(self._device, 'brightness'), errors='replace') as ifile:
                brightness = int(ifile.readline())
        except (IOError, ValueError):
            brightness = 0
        return brightness

    def get_brightness_default(self):
        return int(self._max / 8)

    def get_brightness_max(self):
        try:
            with open(os.path.join(self._device, 'max_brightness'), errors='replace') as ifile:
                brightness = int(ifile.readline())
        except (IOError, ValueError):
            brightness = 0
        return brightness

    def get_brightness_step(self):
        return int(self._max / 24)

    def set_brightness(self, brightness):
        try:
            with open(os.path.join(self._device, 'brightness'), 'w', newline='\n') as ofile:
                print(brightness, file=ofile)
        except IOError:
            pass

    def run(self, change):
        if change:
            if change == '+':
                brightness = min(self.get_brightness() + self._step, self._max)
            elif change == '-':
                brightness = max(self.get_brightness()-self._step, 0)
            elif change == '=':
                brightness = self._default
            self.set_brightness(brightness)
        else:
            print('{0:3.1f} / {1:3.1f}'.format(float(self.get_brightness() + 0.01),
                                               float(self._max + 0.01)))


class BacklightIntel(Backlight):
    """
    Backlight intel class
    """

    def _get_device(self):
        return '/sys/class/backlight/intel_backlight'


class BacklightIntelSetpci(Backlight):
    """
    Backlight Intel (setpci) class
    """

    def detect(self):
        lspci = syslib.Command('lspci', check=False)
        if lspci.is_found():
            lspci.run(filter='VGA.*Intel.*Atom', mode='batch')
            if lspci.has_output():
                self._setpci = syslib.Command(
                    'setpci', flags=['-s', lspci.get_output()[0].split()[0]])
                return True
        return False

    def _get_device(self):
        return None

    def get_brightness(self):
        if syslib.info.get_username() != 'root':
            self._setpci.set_wrapper(syslib.Command('sudo'))
        self._setpci.set_args(['F4.B'])
        self._setpci.run(mode='batch')
        try:
            return int(int(self._setpci.get_output()[0], 16) / 16)  # From 0 - 15
        except (IndexError, ValueError):
            raise SystemExit(sys.argv[0] + ': Cannot detect current brightness setting.')

    def get_brightness_default(self):
        return 3

    def get_brightness_max(self):
        return 15

    def get_brightness_step(self):
        return 1

    def set_brightness(self, brightness):
        self._setpci.set_args(['F4.B={0:x}'.format(brightness*16 + 15)])
        self._setpci.run(mode='exec')


class BacklightXrandr(Backlight):
    """
    Backlight xrandr class
    """

    def detect(self):
        self._xrandr = syslib.Command('xrandr', check=False)
        if self._xrandr.is_found():
            self._xrandr.run(mode='batch')
            self._screens = []
            for line in self._xrandr.get_output('^[^ ]* connected '):
                self._screens.append(line.split()[0])
            if self._screens:
                return True
        return False

    def _get_device(self):
        return None

    def get_brightness(self):
        self._xrandr.set_args(['--verbose'])
        self._xrandr.run(mode='batch')
        try:
            brightness = float(self._xrandr.get_output(r'^\s+Brightness: ')[0].split()[1])
        except (IndexError, ValueError):
            brightness = 0
        return brightness

    def get_brightness_default(self):
        return 0.999

    def get_brightness_max(self):
        return 0.999

    def get_brightness_step(self):
        return 0.1

    def set_brightness(self, brightness):
        for screen in self._screens:
            self._xrandr.set_args(['--output', screen, '--brightness', str(brightness)])
            self._xrandr.run()


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
            options.get_backlight().run(options.get_change())
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
