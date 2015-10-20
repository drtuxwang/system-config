#!/usr/bin/env python3
"""
Rip CD audio tracks as WAVE sound files.
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

        self._icedax = syslib.Command("icedax")

    def getDevice(self):
        """
        Return device location.
        """
        return self._args.device[0]

    def getIcedax(self):
        """
        Return icedax Command class object.
        """
        return self._icedax

    def getSpeed(self):
        """
        Return CD speed.
        """
        return self._args.speed[0]

    def getTracks(self):
        """
        Return list of track numbers.
        """
        return self._tracks

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Rip CD audio tracks as WAVE sound files.")

        parser.add_argument("-speed", nargs=1, type=int, default=[8],
                            help="Select CD spin speed.")
        parser.add_argument("-tracks", nargs=1, metavar="n[,n...]",
                            help="Select CD tracks to rip.")
        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="View CD table of contents only.")

        parser.add_argument("device", nargs=1, metavar="device|scan",
                            help='CD/DVD device (ie "/dev/sr0" or "scan".')

        self._args = parser.parse_args(args)

        if self._args.speed[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "CD/DVD device speed.")
        if self._args.device[0] != "scan" and not os.path.exists(self._args.device[0]):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + self._args.device[0] +
                             '" CD/DVD device.')

        if self._args.tracks:
            self._tracks = self._args.tracks.split(",")
        else:
            self._tracks = None


class Cdrom(syslib.Dump):

    def __init__(self):
        self._devices = {}
        for directory in glob.glob("/sys/block/sr*/device"):
            device = "/dev/" + os.path.basename(os.path.dirname(directory))
            model = ""
            for file in ("vendor", "model"):
                try:
                    with open(os.path.join(directory, file), errors="replace") as ifile:
                        model += " " + ifile.readline().strip()
                except IOError:
                    continue
            self._devices[device] = model

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


class RipCd(syslib.Dump):

    def __init__(self, options):
        self._icedax = options.getIcedax()
        self._device = options.getDevice()
        self._speed = options.getSpeed()
        self._tracks = options.getTracks()

        if self._device == "scan":
            self._scan()
        else:
            self._toc(options)
            if mode == "rip":
                self._rip(options)

    def _rip(self, options):
        self._icedax.setFlags(["-vtrackid", "-paranoia", "-S=" + str(self._speed),
                               "-K", "dsp", "-H"])
        tee = syslib.Command("tee")
        try:
            with open("00.log", "w", newline="\n") as ofile:
                for line in self._toc:
                    print(line, file=ofile)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "00.log" TOC file.')
        try:
            ntracks = int(self._toc[-1].split(".(")[-2].split()[-1])
        except (IndexError, ValueError):
            raise SystemExit(sys.argv[0] + ': Unable to detect the number of audio tracks.')
        if not self._tracks:
            self._tracks = [str(i) for i in range(1, int(ntracks) + 1)]

        for track in self._tracks:
            istrack = re.compile("^.* " + track + "[.]\( *")
            length = "Unknown"
            for line in self._toc:
                if istrack.search(line):
                    minutes, seconds = istrack.sub("", line).split(")")[0].split(":")
                    try:
                        length = "{0:4.2f}".format(int(minutes)*60 + float(seconds))
                    except ValueError:
                        pass
                    break
            logfile = track.zfill(2) + ".log"
            try:
                with open(logfile, "w", newline="\n") as ofile:
                    line = ("\nRipping track " + track + "/" + str(ntracks) +
                            " (" + length + " seconds)")
                    print(line)
                    print(line, file=ofile)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + logfile + '" file.')
            warnfile = track.zfill(2) + ".warning"
            try:
                with open(warnfile, "wb"):
                    pass
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + warnfile + '" file.')
            wavfile = track.zfill(2) + ".wav"
            self._icedax.setArgs(["verbose-level=disable", "track=" + track, "dev=" +
                                  self._device, wavfile, "2>&1"])
            tee.setArgs(["-a", logfile])
            self._icedax.run(pipes=[tee])
            if self._icedax.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(self._icedax.getExitcode()) +
                                 ' received from "' + self._icedax.getFile() + '".')
            if os.path.isfile(wavfile):
                self._pregap(wavfile)
            if not self._hasprob(logfile):
                os.remove(warnfile)

    def _hasprob(self, logfile):
        with open(logfile, errors="replace") as ifile:
            for line in ifile:
                line = line.rstrip("\r\n")
                if line.endswith("problems"):
                    if line[-14:] != "minor problems":
                        ifile.close()
                        return True
        return False

    def _pregap(self, wavfile):
        size = syslib.FileStat(wavfile).getSize()
        with open(wavfile, "rb+") as ifile:
            ifile.seek(size - 2097152)
            data = ifile.read(2097152)
            for i in range(len(data) - 1, 0, -1):
                if data[i] != 0:
                    newsize = size - len(data) + i + 264
                    if newsize < size:
                        line = "Track length is " + str(newsize) + " bytes (pregap removed)"
                        print(line)
                        ifile.truncate(newsize)
                    break

    def _scan(self):
        cdrom = Cdrom()
        print("Scanning for CD/DVD devices...")
        devices = cdrom.getDevices()
        for key, value in sorted(devices.items()):
            print("  {0:10s}  {1:s}".format(key, value))

    def _toc(self, options):
        self._icedax.setArgs(["-info-only", "--no-infofile", "verbose-level=toc",
                              "dev=" + self._device, "speed=" + str(self._speed)])
        self._icedax.run(mode="batch")
        self._toc = self._icedax.getError("[.]\(.*:.*\)")
        if not self._toc:
            raise SystemExit(sys.argv[0] + ": Cannot find Audio CD media. Please check drive.")
        if self._icedax.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._icedax.getExitcode()) +
                             ' received from "' + self._icedax.getFile() + '".')
        for line in self._icedax.getError("[.]\(.*:.*\)|^CD"):
            print(line)


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            RipCd(options)
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
