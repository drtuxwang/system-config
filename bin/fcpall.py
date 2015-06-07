#!/usr/bin/env python3
"""
Copy a file to multiple target files.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import shutil
import signal
import time

import syslib


class Options(syslib.Dump):


    def __init__(self, args):
        self._parseArgs(args[1:])


    def getSource(self):
        """
        Return source file.
        """
        return self._args.source[0]


    def getTargets(self):
        """
        Return target files.
        """
        return self._args.targets


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Copy a file to multiple target files.")

        parser.add_argument("source", nargs=1, help="Source file.")
        parser.add_argument("targets", nargs="+", metavar="target", help="Target file.")

        self._args = parser.parse_args(args)

        if not os.path.isfile(self._args.source[0]):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + self._args.source + '" file.')


class Copy(syslib.Dump):


    def __init__(self, options):
        self._options = options

        source = options.getSource()
        for target in options.getTargets():
            self._copy(source, target)


    def _copy(self, source, target):

            print('Copying to "' + target + '" file...')
            try:
                shutil.copy2(source, target)
            except IOError as exception:
                if exception.args != ( 95, "Operation not supported" ): # os.listxattr for ACL
                    try:
                        with open(source, "rb"):
                            raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" file.')
                    except IOError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" file.')
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot read "' + source + '" file.')
            except shutil.Error as exception:
                if "are the same file" in exception.args[0]:
                    raise SystemExit(sys.argv[0] + ': Cannot copy to same "' + target + '" file.')
                else:
                    raise SystemExit(sys.argv[0] + ': Cannot copy to "' + target + '" file.')


class Main:


    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Copy(options)
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
