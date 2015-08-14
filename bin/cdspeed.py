#!/usr/bin/env python3
"""
Set CD/DVD drive speed.

"$HOME/.config/cdspeed.xml" contains configuration for "cdspeed" utility
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
import xml.dom.minidom

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])

        self._device = syslib.info.getHostname() + ":" + self._args.device[0]

        self._cdspeed()
        if self._speed == 0:
            raise SystemExit(0)

        self._hdparm = syslib.Command(file="/sbin/hdparm",
                                      args=[ "-E", str(self._speed), self._device ])
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
            configfile = os.path.join(configdir, "cdspeed.xml")
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
        if file:
            self._readxml(file)
        else:
            self._default()


    def _addChild(self, node, child, indent=""):
        if node.hasChildNodes():
            node.lastChild.nodeValue = "\n" + indent
        else:
            node.appendChild(self._dom.createTextNode("\n" + indent))
        node.appendChild(child)
        node.appendChild(self._dom.createTextNode("\n" + indent[:-2]))


    def _check(self, file):
        self._version = ""
        for node in self._dom.documentElement.childNodes:
            if node.nodeName == "version":
                self._version = node.getAttribute("value")
                if self._version != "1.00":
                    raise SystemExit(sys.argv[0] + ': Incompatibile version of "' + file +
                                     '" configuration file.')
                break


    def _createDeviceProfile(self, name):
        var = self._dom.createElement("profile")
        var.setAttribute("name", device)
        var.setAttribute("type", "cdrom")
        return var


    def _createSpeedVar(self, speed):
        var = self._dom.createElement("var")
        var.setAttribute("name", "speed")
        var.setAttribute("value", speed)
        return var


    def _default(self):
        self._dom = xml.dom.minidom.parseString("""\
<cdspeed>
    <version value = "1.00"/>
</cdspeed>
""")
        self._version = "1.00"


    def _readxml(self, file):
        try:
            self._dom = xml.dom.minidom.parse(file)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" XML file.')
        except xml.parsers.expat.ExpatError as exception:
            raise SystemExit(sys.argv[0] + ': Invalid XML "' + file + ': ' + str(exception) + '".')
        if self._dom.documentElement.nodeName != "cdspeed":
            raise SystemExit(sys.argv[0] + ': Incorrect format of "' + file +
                             '" configuration file.')
        self._check(file)


    def getSpeed(self, device):
        for profile in self._dom.documentElement.childNodes:
            if profile.nodeName == "profile":
                if profile.getAttribute("type") == "cdrom":
                    if profile.getAttribute("name") == device:
                        for var in profile.childNodes:
                            if var.nodeName == "var":
                                if var.getAttribute("name") == "speed":
                                    try:
                                        return int(var.getAttribute("value"))
                                    except ValueError:
                                        return 0
        return None


    def setSpeed(self, device, speed):
        for profile in self._dom.documentElement.childNodes:
            if profile.nodeName == "profile":
                if profile.getAttribute("type") == "cdrom":
                    if profile.getAttribute("name") == device:
                        for var in profile.childNodes:
                            if var.nodeName == "var":
                                if var.getAttribute("name") == "speed":
                                    var.setAttribute("value", str(speed))
                                    return
                        self._addChild(profile, self._createSpeedVar(speed), indent="    ")
                        return
        profile = self._dom.createElement("profile")
        profile.setAttribute("name", device)
        profile.setAttribute("type", "cdrom")
        self._addChild(self._dom.documentElement, profile, indent="  ")
        self._addChild(profile, self._createSpeedVar(speed), indent="    ")


    def write(self, file):
        self._dom.writexml(WriteXml(file))


class WriteXml(syslib.Dump):


    def __init__(self, file):
        try:
            self._ofile = open(file, "w", newline="\n")
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '" XML file.')


    def __del__(self):
        print(file=self._ofile)
        self._ofile.close()


    def write(self, text):
        print(text, end="", file=self._ofile)
        if text.startswith("<?xml version="):
            print(file=self._ofile)


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
