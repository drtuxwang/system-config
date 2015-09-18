#!/usr/bin/env python3
"""
Set CD/DVD drive speed.

"$HOME/.config/cdspeed.json" contain configuration information.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import json
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._device = syslib.info.getHostname() + ":" + self._args.device[0]

        self._cdspeed()
        if self._speed == 0:
            raise SystemExit(0)

        self._hdparm = syslib.Command(file="/sbin/hdparm",
                                      args=["-E", str(self._speed), self._device])
        print("Setting CD/DVD drive speed to ", self._speed, "X", sep="")

    def getHdparm(self):
        """
        Return hdparm Command class object.
        """
        return self._hdparm

    def _cdspeed(self):
        if "HOME" in os.environ.keys():
            configdir = os.path.join(os.environ["HOME"], ".config")
            if not os.path.isdir(configdir):
                try:
                    os.mkdir(configdir)
                except OSError:
                    return
            configfile = os.path.join(configdir, "cdspeed.json")
            if os.path.isfile(configfile):
                config = Configuration(configfile)
                speed = config.getSpeed(self._device)
                if speed:
                    if self._speed == 0:
                        self._speed = speed
                    elif self._speed == speed:
                        return
            else:
                config = Configuration()
            config.setSpeed(self._device, self._speed)
            config.write(configfile + "-new")
            try:
                os.rename(configfile + "-new", configfile)
            except OSError:
                os.remove(configfile + "-new")

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Set CD/DVD drive speed.")

        parser.add_argument("device", nargs=1, help='CD/DVD device (ie "/dev/sr0").')
        parser.add_argument("speed", nargs="?", type=int, help="Select CD/DVD spin speed.")

        self._args = parser.parse_args(args)

        if self._args.speed:
            self._speed = self._args.speed
            if self._speed < 0:
                raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                                 "CD/DVD device speed.")
        else:
            self._speed = 0


class Configuration(syslib.Dump):

    def __init__(self, file=""):
        self._data = {"cdspeed": {}}
        if file:
            try:
                with open(file) as ifile:
                    self._data = json.load(ifile)
            except (IOError, KeyError):
                pass

    def getSpeed(self, device):
        try:
            return self._data["cdspeed"][device]
        except KeyError:
            return 0

    def setSpeed(self, device, speed):
        self._data["cdspeed"][device] = speed

    def write(self, file):
        try:
            with open(file, "w", newline="\n") as ofile:
                print(json.dumps(self._data, indent=4, sort_keys=True), file=ofile)
        except IOError:
            pass


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getHdparm().run(mode="batch")
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getHdparm().getExitcode())

    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
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


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
