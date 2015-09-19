#!/usr/bin/env python3
"""
JAVA jar tool launcher
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._jar = syslib.Command(os.path.join("bin", "jar"))

        if len(args) == 1:
            self._jar.run(mode="exec")
        elif args[1][-4:] != ".jar":
            self._jar.setArgs(args[1:])
            self._jar.run(mode="exec")

        self._jarFile = args[1]
        self._manifest = args[1][:-4]+".manifest"
        self._files = args[2:]
        self._jar.setFlags(["cfvm", args[1], self._manifest])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._files

    def getJar(self):
        """
        Return jar Command class object.
        """
        return self._jar

    def getJarFile(self):
        """
        Return jar file location.
        """
        return self._jarFile

    def getManifest(self):
        """
        Return manifest file location.
        """
        return self._manifest


class Pack(syslib.Dump):

    def __init__(self, options):
        self._jar = options.getJar()
        self._jarFile = options.getJarFile()
        self._manifest = options.getManifest()

        for file in options.getFiles():
            if file.endswith(".java"):
                self._compile(file)
                self._jar.appendArg(file[:-5]+".class")
            else:
                self._jar.appendArg(file)
        self._createManifest(options)
        print('Building "' + self._jarFile + '" Java archive file.')
        self._jar.run(mode="exec")

    def _compile(self, source):
        target = source[:-5]+".class"
        if not os.path.isfile(source):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + source + '" Java source file.')
        if os.path.isfile(target):
            if syslib.FileStat(source).getTime() > syslib.FileStat(target).getTime():
                try:
                    os.remove(target)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot remove "' +
                                     target + '" Java class file.')
        if not os.path.isfile(target):
            javac = syslib.Command("javac", args=[source])
            print('Building "' + target + '" Java class file.')
            javac.run(mode="batch", error2output=True)
            if javac.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(javac.getExitcode()) +
                                 ' received from "' + javac.getFile() + '".')
            for line in javac.getOutput():
                print("  " + line)
            if not os.path.isfile(target):
                raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" Java class file.')

    def _createManifest(self, options):
        if not os.path.isfile(self._manifest):
            if "Main.class" in self._jar.getArgs():
                main = "Main"
            else:
                main = self._jarFile[:-4]
            print('Building "' + self._manifest + '" Java manifest file with "' +
                  main + '" main class.')
            try:
                with open(self._manifest, "w", newline="\n") as ofile:
                    print("Main-Class:", main, file=ofile)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                 self._manifest + '" Java manifest file.')


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Pack(options)
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
