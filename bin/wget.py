#!/usr/bin/env python3
"""
Wrapper for "wget" command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import json
import os
import signal

import netnice
import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._wget = syslib.Command("wget")
        self._wget.setFlags([ "--no-check-certificate", "--timestamping" ])

        shaper = netnice.Shaper()
        if shaper.isFound():
            self._wget.setWrapper(shaper)

        self._output = ""
        while len(args) > 1:
            if (len(args) > 2 and args[1] in ( "--output-document", "-O" ) and
                    not args[2].endswith(".part")):
                self._output =  args[2]
                if os.path.isfile(args[2]) or os.path.isfile(args[2] + ".part"):
                    self._output = ("-"+str(os.getpid())+".").join(self._output.rsplit(".",1))
                self._wget.extendArgs([ args[1], self._output + ".part" ])
                args = args[2:]
                continue
            self._wget.appendArg(args[1])
            args = args[1:]

        self._setProxy()


    def getOutput(self):
        """
        Return output file.
        """
        return self._output


    def getWget(self):
        """
        Return wget Command class object.
        """
        return self._wget


    def _setProxy(self):
        setproxy = syslib.Command("setproxy", check=False)
        if setproxy.isFound():
            setproxy.run(mode="batch")
            if not setproxy.getExitcode() and setproxy.hasOutput():
                proxy = setproxy.getOutput()[0].strip()
                if proxy:
                    os.environ["ftp_proxy"] = "http://" + proxy
                    os.environ["http_proxy"] = "http://" + proxy
                    os.environ["https_proxy"] = "http://" + proxy


class Download(syslib.Dump):


    def __init__(self, options):
        self._output = options.getOutput()
        self._wget = options.getWget()


    def run(self):
        if self._output:
            self._wget.run()
            if self._wget.getExitcode():
                raise SystemExit(self._wget.getExitcode())
            try:
                os.rename(self._output + ".part", self._output)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                 self._output + '" output file.')
        else:
            self._wget.run(mode="exec")


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Download(options).run()
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
