#!/usr/bin/env python3
"""
Rip Video DVD title to file.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])

        self.dump("options.")
        self._vlc = syslib.Command("vlc")


    def getDevice(self):
        """
        Return device location.
        """
        return self._args.device[0]


    def getVlc(self):
        """
        Return vlc Command class object.
        """
        return self._vlc


    def getSpeed(self):
        """
        Return DVD speed.
        """
        return self._args.speed[0]


    def getTitle(self):
        """
        Return DVD title.
        """
        return self._args.title[0]


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Rip Video DVD title to file.")

        parser.add_argument("-speed", nargs=1, type=int, default=[ 8 ],
                            help="Select DVD spin speed.")
        parser.add_argument("-title", nargs=1, type=int, default=[ 1 ],
                            help="Select DVD title to rip (Default is 1).")

        parser.add_argument("device", nargs=1, metavar="device|scan",
                            help='DVD device (ie "/dev/sr0" or "scan".')

        self._args = parser.parse_args(args)

        if self._args.speed[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "DVD device speed.")
        if self._args.title[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for DVD title.")
        if self._args.device[0] != "scan" and not os.path.exists(self._args.device[0]):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + self._args.device[0] +
                             '" DVD device.')


class Cdrom(syslib.Dump):


    def __init__(self):
        self._devices = {}
        for directory in glob.glob("/sys/block/sr*/device"):
            device = "/dev/" + os.path.basename(os.path.dirname(directory))
            model = ""
            for file in ( "vendor", "model" ):
                try:
                    with open(os.path.join(directory, file), errors="replace") as ifile:
                        model += " " + ifile.readline().strip()
                except IOError:
                    continue
            self._devices[ device ] = model


    def device(self, mount):
        if mount == "cdrom":
            rank = 0
        else:
            try:
                rank = int(mount[5:])-1
            except ValueError:
                return ""
        try:
            return sorted(self._devices.keys())[rank]
        except IndexError:
            return ""


    def getDevices(self):
        """
        Return list of devices
        """
        return self._devices


class RipDvd(syslib.Dump):


    def __init__(self, options):
        self._vlc = options.getVlc()
        self._device = options.getDevice()
        self._speed = options.getSpeed()
        self._title = options.getTitle()

        if self._device == "scan":
            self._scan()
        else:
            self._cdspeed(self._device, options.getSpeed())
            self._rip(options)


    def _cdspeed(self, device, speed):
        cdspeed = syslib.Command("cdspeed", flags=[ device ], check=False)
        if cdspeed.isFound():
            if speed:
                cdspeed.setArgs([ str(speed) ])
            # If CD/DVD spin speed change fails its okay
            cdspeed.run()
        elif speed:
            hdparm = syslib.Command(file="/sbin/hdparm", args=[ "-E", str(speed), device ])
            hdparm.run(mode="batch")


    def _rip(self, options):
        file = "title-" + str(self._title).zfill(2) + ".mpg"
        self._vlc.setArgs([ "dvdsimple:/" + self._device + ":#" + str(self._title),
                            "--sout", "#standard{access=file,mux=ts,dst=" + file + "}",
                            "vlc://quit" ])
        self._vlc.run()


    def _scan(self):
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.getDevices()
        for key in sorted(devices.keys()):
            print("  {0:10s}  {1:s}".format(key, devices[key]))


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            RipDvd(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)


    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg) # Fixes Windows globbing bug
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
