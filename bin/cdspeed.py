#!/usr/bin/env python3
"""
Set CD/DVD drive speed.

'$HOME/.config/cdspeed.json' contain configuration information.
"""

import argparse
import glob
import json
import os
import shutil
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_hdparm(self):
        """
        Return hdparm Command class object.
        """
        return self._hdparm

    def _config_speed(self):
        if self._args.speed:
            speed = self._args.speed
            if speed < 0:
                raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                                 'CD/DVD device speed.')
        else:
            speed = 0

        if 'HOME' in os.environ:
            configdir = os.path.join(os.environ['HOME'], '.config')
            if not os.path.isdir(configdir):
                try:
                    os.mkdir(configdir)
                except OSError:
                    return
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
            config.write(configfile + '-new')
            try:
                shutil.move(configfile + '-new', configfile)
            except OSError:
                os.remove(configfile + '-new')

            return speed

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Set CD/DVD drive speed.')

        parser.add_argument('device', nargs=1, help="CD/DVD device (ie '/dev/sr0').")
        parser.add_argument('speed', nargs='?', type=int, help='Select CD/DVD spin speed.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._device = syslib.info.get_hostname() + ':' + self._args.device[0]

        self._speed = self._config_speed()
        if self._speed == 0:
            raise SystemExit(0)

        self._hdparm = syslib.Command(file='/sbin/hdparm',
                                      args=['-E', str(self._speed), self._device])
        print('Setting CD/DVD drive speed to ', self._speed, 'X', sep='')


class Configuration(object):
    """
    Configuration class
    """

    def __init__(self, file=''):
        self._data = {'cdspeed': {}}
        if file:
            try:
                with open(file) as ifile:
                    self._data = json.load(ifile)
            except (KeyError, OSError):
                pass

    def get_speed(self, device):
        """
        Get speed
        """
        try:
            return self._data['cdspeed'][device]
        except KeyError:
            return 0

    def set_speed(self, device, speed):
        """
        Set speed
        """
        self._data['cdspeed'][device] = speed

    def write(self, file):
        """
        Write file
        """
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(self._data, indent=4, sort_keys=True), file=ofile)
        except OSError:
            pass


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

        options.get_hdparm().run(mode='batch')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
