#!/usr/bin/env python3
"""
Desktop screen backlight utility.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._backlight = self._getBacklight()

    def getChange(self):
        """
        Return change.
        """
        return self._args.change

    def getBacklight(self):
        """
        Return BacklightXXX class object.
        """
        return self._backlight

    def _getBacklight(self):
        for backlight in (BacklightIntel(), BacklightIntelSetpci(), BacklightXrandr()):
            if backlight.detect():
                return backlight
        raise SystemExit(sys.argv[0] + ": Cannot detect backlight device.")

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Desktop screen backlight utility.')

        parser.add_argument('-dec', action='store_const', const='-', dest='change',
                            help='Increase brightness.')
        parser.add_argument('-inc', action='store_const', const='+', dest='change',
                            help='Default brightness.')
        parser.add_argument('-reset', action='store_const', const='=', dest='change',
                            help='Decrease brightness.')

        self._args = parser.parse_args(args)


class Backlight:

    def __init__(self):
        self._device = self._getDevice()
        self._max = self.getBrightnessMax()
        self._default = self.getBrightnessDefault()
        self._step = self.getBrightnessStep()

    def detect(self):
        file = os.path.join(self._device, 'brightness')
        if os.path.isfile(file):
            if syslib.info.getUsername() != 'root':
                try:
                    os.chmod(file, int('666', 8))
                except OSError:
                    pass
            return True
        return False

    def _getDevice(self):
        return '/sys/class/backlight/acpi_video0'

    def getBrightness(self):
        try:
            with open(os.path.join(self._device, 'brightness'), errors='replace') as ifile:
                brightness = int(ifile.readline())
        except (IOError, ValueError):
            brightness = 0
        return brightness

    def getBrightnessDefault(self):
        return int(self._max / 8)

    def getBrightnessMax(self):
        try:
            with open(os.path.join(self._device, 'max_brightness'), errors='replace') as ifile:
                brightness = int(ifile.readline())
        except (IOError, ValueError):
            brightness = 0
        return brightness

    def getBrightnessStep(self):
        return int(self._max / 24)

    def setBrightness(self, brightness):
        try:
            with open(os.path.join(self._device, 'brightness'), 'w', newline='\n') as ofile:
                print(brightness, file=ofile)
        except IOError:
            pass

    def run(self, change):
        if change:
            if change == '+':
                brightness = min(self.getBrightness() + self._step, self._max)
            elif change == '-':
                brightness = max(self.getBrightness()-self._step, 0)
            elif change == '=':
                brightness = self._default
            self.setBrightness(brightness)
        else:
            print('{0:3.1f} / {1:3.1f}'.format(float(self.getBrightness() + 0.01),
                                               float(self._max + 0.01)))


class BacklightIntel(Backlight):

    def _getDevice(self):
        return '/sys/class/backlight/intel_backlight'


class BacklightIntelSetpci(Backlight):

    def detect(self):
        lspci = syslib.Command('lspci', check=False)
        if lspci.isFound():
            lspci.run(filter='VGA.*Intel.*Atom', mode='batch')
            if lspci.hasOutput():
                self._setpci = syslib.Command(
                    'setpci', flags=['-s', lspci.getOutput()[0].split()[0]])
                return True
        return False

    def _getDevice(self):
        return None

    def getBrightness(self):
        if syslib.info.getUsername() != 'root':
            self._setpci.setWrapper(syslib.Command('sudo'))
        self._setpci.setArgs(['F4.B'])
        self._setpci.run(mode='batch')
        try:
            return int(int(self._setpci.getOutput()[0], 16) / 16)  # From 0 - 15
        except (IndexError, ValueError):
            raise SystemExit(sys.argv[0] + ': Cannot detect current brightness setting.')

    def getBrightnessDefault(self):
        return 3

    def getBrightnessMax(self):
        return 15

    def getBrightnessStep(self):
        return 1

    def setBrightness(self, brightness):
        self._setpci.setArgs(['F4.B={0:x}'.format(brightness*16 + 15)])
        self._setpci.run(mode='exec')


class BacklightXrandr(Backlight):

    def detect(self):
        self._xrandr = syslib.Command('xrandr', check=False)
        if self._xrandr.isFound():
            self._xrandr.run(mode='batch')
            self._screens = []
            for line in self._xrandr.getOutput('^[^ ]* connected '):
                self._screens.append(line.split()[0])
            if self._screens:
                return True
        return False

    def _getDevice(self):
        return None

    def getBrightness(self):
        self._xrandr.setArgs(['--verbose'])
        self._xrandr.run(mode='batch')
        try:
            brightness = float(self._xrandr.getOutput('^\s+Brightness: ')[0].split()[1])
        except (IndexError, ValueError):
            brightness = 0
        return brightness

    def getBrightnessDefault(self):
        return 0.999

    def getBrightnessMax(self):
        return 0.999

    def getBrightnessStep(self):
        return 0.1

    def setBrightness(self, brightness):
        for screen in self._screens:
            self._xrandr.setArgs(['--output', screen, '--brightness', str(brightness)])
            self._xrandr.run()


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getBacklight().run(options.getChange())
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
