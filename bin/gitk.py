#!/usr/bin/env python3
"""
Wrapper for GITK revision control system
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
        self._gitk = syslib.Command(os.path.join("bin", "gitk"))
        self._gitk.setArgs(args[1:])

        self._env = {}
        if os.name == "nt":
            os.environ["PATH"] = os.path.join(os.environ["PATH"],
                                              os.path.dirname(self._gitk.getFile()))
        else:
            gitHome = os.path.dirname(os.path.dirname(self._gitk.getFile()))
            if gitHome not in ("/usr", "/usr/local"):
                self._env["GIT_EXEC_PATH"] = os.path.join(gitHome, "libexec", "git-core")
                self._env["GIT_TEMPLATE_DIR"] = os.path.join(gitHome, "share",
                                                             "git-core", "templates")

        self._config()

    def getEnv(self):
        """
        Return dictionary of environments.
        """
        return self._env

    def getGitk(self):
        """
        Return gitk Command class object.
        """
        return self._gitk

    def _config(self):
        if "HOME" in os.environ.keys():
            file = os.path.join(os.environ["HOME"], ".gitconfig")
            if not os.path.isfile(file):
                try:
                    with open(file, "w", newline="\n") as ofile:
                        user = syslib.info.getUsername()
                        host = syslib.info.getHostname()
                        print("[user]", file=ofile)
                        print("        name =", user, file=ofile)
                        print("        email =", user + "@" + host, file=ofile)
                except IOError:
                    pass


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getGitk().run(mode="exec", env=options.getEnv())
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
