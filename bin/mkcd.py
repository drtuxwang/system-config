#!/usr/bin/env python3
"""
Make data/audio/video CD/DVD using CD/DVD writer.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal
import time

import syslib


class Options(syslib.Dump):


    def __init__(self, args):

        self._parseArgs(args[1:])

        if self._args.image != "scan":
            self._deviceDetect()
        self._signalTrap()


    def getDevice(self):
        """
        Return device location.
        """
        return self._device


    def getEraseFlag(self):
        """
        Return erase flag.
        """
        return self._args.eraseFlag


    def getImage(self):
        """
        Return ISO/BIN image file or audio directory.
        """
        return self._args.image[0]


    def getMd5Flag(self):
        """
        Return md5 flag.
        """
        return self._args.md5Flag[0]


    def getSpeed(self):
        """
        Return CD speed.
        """
        return self._args.speed[0]


    def _deviceDetect(self):
        if self._args.device:
            self._device = self._args.device[0]
        else:
            cdrom = Cdrom()
            if not cdrom.getDevices().keys():
                raise SystemExit(sys.argv[0] + ": Cannot find any CD/DVD device.")
            self._device = sorted(cdrom.getDevices().keys())[0]
        if not os.path.exists(self._device) and  not os.path.isdir(self._image):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + self._device + '" CD/DVD device.')


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
                description="Make data/audio/video CD/DVD using CD/DVD writer.")

        parser.add_argument("-dev", nargs=1, dest="device",
                            help="Select device (ie /dev/sr0).")
        parser.add_argument("-erase", dest="eraseFlag", action="store_true",
                            help="Erase TOC on CD-RW media before writing in DAO mode.")
        parser.add_argument("-md5", dest="md5Flag", action="store_true",
                            help="Verify MD5 check sum of data CD/DVD disk.")
        parser.add_argument("-speed", nargs=1, type=int, default=[ 8 ],
                            help="Select CD/DVD spin speed.")

        parser.add_argument("image", nargs=1, metavar="image.iso|image.bin|directory|scan",
                            help="ISO/BIn image file, audio or scan")

        self._args = parser.parse_args(args)

        if self._args.speed[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "CD/DVD device speed.")
        if self._args.image[0] != "scan" and not os.path.isdir(self._args.image[0]):
            if not os.path.exists(self._args.image[0]):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + self._args.image[0] +
                                 '" CD/DVD device.')


    def _signalIgnore(self, signal, frame):
        pass


    def _signalTrap(self):
        signal.signal(signal.SIGINT, self._signalIgnore)
        signal.signal(signal.SIGTERM, self._signalIgnore)


class Burner(syslib.Dump):


    def __init__(self, options):
        self._device = options.getDevice()
        self._speed = options.getSpeed()
        self._image = options.getImage()

        if self._image == "scan":
            self._scan()
        elif os.path.isdir(self._image):
            self._trackAtOnceAudio(options)
        elif self._image.endswith(".bin"):
            self._diskAtOnceData(options)
        else:
            self._trackAtOnceData(options)


    def _eject(self):
        eject = syslib.Command("eject", check=False)
        if eject.isFound():
            time.sleep(1)
            eject.run(mode="batch")
            if eject.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(eject.getExitcode()) +
                                 ' received from "' + eject.getFile() + '".')


    def _scan(self):
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.getDevices()
        for key in sorted(devices.keys()):
            print("  {0:10s}  {1:s}".format(key, devices[key]))


    def _diskAtOnceData(self, options):
        cdrdao = syslib.Command("cdrdao")
        if options.getEraseFlag():
            cdrdao.setArgs([ "blank", "--blank-mode", "minimal", "--device", self._device,
                             "--speed", str(self._speed) ])
            cdrdao.run()
            if cdrdao.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(cdrdao.getExitcode()) +
                                 ' received from "' +  cdrdao.getFile() + '".')
        cdrdao.setFlags([ "write", "--device", self._device, "--speed", str(self._speed) ])
        if os.path.isfile(self._files[0][:-4]+".toc"):
            cdrdao.setArgs([ self._files[0][:-4]+".toc" ])
        else:
            cdrdao.setArgs([ self._files[0][:-4]+".cue" ])
        cdrdao.run()
        if cdrdao.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(cdrdao.getExitcode()) +
                             ' received from "' + cdrdao.getFile() + '".')
        self._eject()


    def _trackAtOnceAudio(self, options):
        files = glob.glob(os.path.join(self._image[0], "*.wav"))

        wodim = syslib.Command("wodim")
        print("If your media is a rewrite-able CD/DVD its contents will be deleted.")
        answer = input("Do you really want to burn data to this CD/DVD disk? (y/n) [n] ")
        if answer.lower() != "y":
            raise SystemExit(1)
        print("Using AUDIO mode for WAVE files (Audio tracks detected)...")
        wodim.setArgs([ "-v", "-shorttrack", "-audio", "-pad", "-copy", "dev=" + self._device,
                        "speed=" + str(self._speed), "driveropts=burnfree" ] + files)
        wodim.run()
        if wodim.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(wodim.getExitcode()) +
                             ' received from "' + wodim.getFile() + '".')

        time.sleep(1)
        icedax = syslib.Command("icedax", check=False)
        if icedax.isFound():
            icedax.setArgs([ "-info-only", "--no-infofile", "verbose-level=toc",
                             "dev=" + self._device, "speed=" + self._speed ])
            icedax.run(mode="batch")
            toc = icedax.getError("[.]\(.*:.*\)|^CD")
            if not toc:
                raise SystemExit(sys.argv[0] + ": Cannot find Audio CD media. Please check drive.")
            elif icedax.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(icedax.getExitcode()) +
                                 ' received from "' + icedax.getFile() + '".')
            for line in toc:
                print(line)
        self._eject()


    def _trackAtOnceData(self, options):
        file = options.getImage()

        wodim = syslib.Command("wodim")
        print("If your media is a rewrite-able CD/DVD its contents will be deleted.")
        answer = input("Do you really want to burn data to this CD/DVD disk? (y/n) [n] ")
        if answer.lower() != "y":
            raise SystemExit(1)
        wodim.setFlags([ "-v", "-shorttrack", "-eject" ])
        if syslib.FileStat(file).getSize() < 2097152: # Pad to avoid dd read problem
            wodim.appendArg("-pad")
        wodim.setArgs([ "dev=" + self._device, "speed=" + str(self._speed),
                        "driveropts=burnfree", file ])
        wodim.run()
        if wodim.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(wodim.getExitcode()) +
                             ' received from "' + wodim.getFile() + '".')

        if options.getMd5cdFlag():
            print("Verifying MD5 check sum of data CD/DVD:")
            dd = syslib.Command("dd")
            dd.setArgs([ "if=" + self._device, "bs=" + str(2048*360), "count=1", "of=/dev/null" ])
            for i in range(10):
                time.sleep(1)
                dd.run(mode="batch")
                if dd.hasOutput():
                    time.sleep(1)
                    break
            md5cd = syslib.Command("md5cd", args=[ self._device ])
            md5cd.run()
            if md5cd.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(md5cd.getExitcode()) +
                                 ' received from "' + md5cd.getFile() + '".')
            try:
                with open(self._files[0][:-4] + ".md5", errors="replace") as ifile:
                    for line in ifile:
                        print(line.rstrip())
            except IOError:
                pass


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
        Return list of devices.
        """
        return self._devices


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Burner(options)
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
