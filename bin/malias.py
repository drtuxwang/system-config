#!/usr/bin/env python3
"""
Look up mail aliases in ".mailrc" file.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
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

        self._domainName = ""
        if "HOME" in os.environ.keys():
            try:
                with open(os.path.join(os.environ["HOME"], ".address"), errors="replace") as ifile:
                     self._domainName = ifile.readline().strip().split("@")[-1]
            except IOError:
                pass
        if not self._domainName:
            domainName = syslib.Command("domainname")
            domainName.run(mode="batch")
            if domainName.hasOutput():
                self._domainName = domainName.getOutput()[0]


    def getAliases(self):
        """
        Return list of aliases.
        """
        return self._args.aliases


    def getDomainName(self):
        """
        Return domain name.
        """
        return self._domainName

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Look up mail aliases in ".mailrc" file.')

        parser.add_argument("aliases", nargs="+", metavar="alias", help="E-mail alias.")

        self._args = parser.parse_args(args)


class Address(syslib.Dump):


    def __init__(self):
        self._names = []
        self._book = {}
        if "HOME" in os.environ.keys():
            try:
                with open(os.path.join(os.environ["HOME"], ".mailrc"), errors="replace") as ifile:
                    iscomment = re.compile("^( |\t)*#")
                    for line in ifile:
                        if not iscomment.match(line):
                            if len(line.split()) == 2:
                                name, address = line.strip().split()
                                self._book[name] = address
                                self._names.append(name)
            except IOError:
                pass


    def match(self, domainname, aliases):
        addresses = []
        for alias in aliases:
            try:
                isMatch = re.compile(alias, re.IGNORECASE)
            except re.error:
                raise SystemExit(sys.argv[0] + ': Invalid regular expression "' + alias + '".')
            if "@" in alias:
                addresses.append(alias)
            else:
                address = alias + "@" + domainname
                for name in self._names:
                    if isMatch.search(name):
                        address = self._book[name]
                        break
                addresses.append(address)
        print(",".join(addresses))


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Address().match(options.getDomainName(), options.getAliases())
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
