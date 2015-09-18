#!/usr/bin/env python3
"""
Edit multiple files.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        if os.path.isfile("/usr/bin/vim"):
            self._editor = syslib.Command(file="/usr/bin/vim", flags=["-N", "-n", "-u", "NONE"])
        else:
            self._editor = syslib.Command("vi")
        self._speller = syslib.Command("fspell")

    def getEditor(self):
        """
        Return editor Command class object.
        """
        return self._editor

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getSpeller(self):
        """
        Return speller Command class object.
        """
        return self._speller

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Edit multiple files.")

        parser.add_argument("files", nargs="+", metavar="file", help="File to edit.")

        self._args = parser.parse_args(args)


class Edit(syslib.Dump):

    def __init__(self, options):
        self._options = options
        files = options.getFiles()
        speller = options.getSpeller()

        self._edit(files[0])

        while files:
            print("\n" + str(len(files)), "files =", str(files).replace("u'", "'") + "\n")
            answer = input(" e = Edit   s = Spell check   n = Skip file   q = Quit : ")
            if answer.startswith("e"):
                self._edit(files[0])
            elif answer.startswith("n"):
                files = files[1:]
            elif answer.startswith("q"):
                break
            elif answer.startswith("s"):
                speller.setArgs(files[:1])
                speller.run()
                try:
                    os.remove(files[0]+".bak")
                except OSError:
                    pass

    def _edit(self, file):
        self._options.getEditor().setArgs([file])
        sys.stdout.write("\033]0;" + syslib.info.getHostname() + ":" +
                         os.path.abspath(file) + "\007")
        sys.stdout.flush()
        self._options.getEditor().run()
        sys.stdout.write("\033]0;" + syslib.info.getHostname() + ":" + os.getcwd() + "\007")


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Edit(options)
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
