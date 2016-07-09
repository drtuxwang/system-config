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

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

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

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Desktop screen backlight utility.')

        parser.add_argument('-dec', action='store_const', const='-', dest='change',
                            help='Increase brightness.')
        parser.add_argument('-inc', action='store_const', const='+', dest='change',
                            help='Default brightness.')
        parser.add_argument('-reset', action='store_const', const='=', dest='change',
                            help='Decrease brightness.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._backlight = Backlight.factory()


class Backlight(object):
    """
    Backlight base class
    """

    def __init__(self):
        self._device = self._get_device()
        self._max = self.get_brightness_max()
        self._default = self.get_brightness_default()
        self._step = self.get_brightness_step()

        self._command = None
        self._screens = None

    @staticmethod
    def factory():
        """
        Return Backlight sub class object
        """
        for backlight in (BacklightIntel(), BacklightIntelSetpci(), BacklightXrandr()):
            if backlight.detect():
                return backlight
        raise SystemExit(sys.argv[0] + ": Cannot detect backlight device.")

    @staticmethod
    def _get_device():
        return '/sys/class/backlight/acpi_video0'

    def get_brightness(self):
        """
        Return brightness
        """
        try:
            with open(os.path.join(self._device, 'brightness'), errors='replace') as ifile:
                brightness = int(ifile.readline())
        except (OSError, ValueError):
            brightness = 0
        return brightness

    def get_brightness_default(self):
        """
        Return brightness default
        """
        return int(self._max / 8)

    def get_brightness_max(self):
        """
        Return brightness max
        """
        try:
            with open(os.path.join(self._device, 'max_brightness'), errors='replace') as ifile:
                brightness = int(ifile.readline())
        except (OSError, ValueError):
            brightness = 0
        return brightness

    def get_brightness_step(self):
        """
        Return brightness step size
        """
        return int(self._max / 24)

    def set_brightness(self, brightness):
        """
        set brightness
        """
        try:
            with open(os.path.join(self._device, 'brightness'), 'w', newline='\n') as ofile:
                print(brightness, file=ofile)
        except OSError:
            pass

    def detect(self):
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

    def run(self, change):
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

    def _get_device(self):
        return None

    def get_brightness(self):
        """
        Return brightness
        """
        if getpass.getuser() != 'root':
            hostname = socket.gethostname().split('.')[0].lower()
            username = getpass.getuser()
            prompt = '[sudo] password for {0:s}@{1:s}: '.format(hostname, username)
            sudo = command_mod.Command('sudo', errors='stop')
            sudo.set_args(['-p', prompt])
            task = subtask_mod.Batch(sudo.get_cmdline() + self._command.get_cmdline() + ['F4.B'])
        else:
            task = subtask_mod.Batch(self._command.get_cmdline() + ['F4.B'])
        task.run()
        try:
            return int(int(task.get_output()[0], 16) / 16)  # From 0 - 15
        except (IndexError, ValueError):
            raise SystemExit(sys.argv[0] + ': Cannot detect current brightness setting.')

    def get_brightness_default(self):
        """
        Return brightness default
        """
        return 3

    def get_brightness_max(self):
        """
        Return brightness max
        """
        return 15

    def get_brightness_step(self):
        """
        Return brightness step size
        """
        return 1

    def set_brightness(self, brightness):
        """
        Set brightness
        """
        self._command.set_args(['F4.B={0:x}'.format(brightness*16 + 15)])
        subtask_mod.Exec(self._command.get_cmdline()).run()

    def detect(self):
        """
        Detect status
        """
        lspci = command_mod.Command('lspci', errors='ignore')
        if lspci.is_found():
            task = subtask_mod.Batch(lspci.get_cmdline())
            task.run(pattern='VGA.*Intel.*Atom')
            if task.has_output():
                self._command = command_mod.Command(
                    'setpci', args=['-s', task.get_output()[0].split()[0]], errors='stop')
                return True
        return False


class BacklightXrandr(Backlight):
    """
    Backlight xrandr class
    """

    def _get_device(self):
        return None

    def get_brightness(self):
        """
        Return brightness
        """
        self._command.set_args(['--verbose'])
        task = subtask_mod.Batch(self._command.get_cmdline())
        task.run()
        try:
            brightness = float(task.get_output(r'^\s+Brightness: ')[0].split()[1])
        except (IndexError, ValueError):
            brightness = 0.
        return brightness

    def get_brightness_default(self):
        """
        Return brightness default
        """
        return 0.999

    def get_brightness_max(self):
        """
        Return brightness max
        """
        return 0.999

    def get_brightness_step(self):
        """
        Return brightness step size
        """
        return 0.1

    def set_brightness(self, brightness):
        """
        Set brightness
        """
        for screen in self._screens:
            self._command.set_args(['--output', screen, '--brightness', str(brightness)])
            subtask_mod.Task(self._command.get_cmdline()).run()

    def detect(self):
        """
        Detect status
        """
        self._command = command_mod.Command('xrandr', errors='ignore')
        if self._command.is_found():
            task = subtask_mod.Batch(self._command.get_cmdline())
            task.run()
            self._screens = []
            for line in task.get_output('^[^ ]* connected '):
                self._screens.append(line.split()[0])
            if self._screens:
                return True
        return False


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

        options.get_backlight().run(options.get_change())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
