#!/usr/bin/env python3
"""
Wrapper for "firefox" command

Use "-copy" to copy profile to "/tmp" and use "-no-remote about:"
Use "-no-remote" to avoid using current instance
Use "-reset" to clean junk from profile
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ": Requires Python version (>= 3.0, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import re
import shutil
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        # firefox10 etc
        self._firefox = syslib.Command(os.path.basename(args[0]).replace(".py", ""))
        updates = os.access(self._firefox.getFile(), os.W_OK)

        while len(args) > 1:
            if not args[1].startswith("-"):
                break
            elif args[1] == "-copy":
                updates = False
                self._copy()
                self._firefox.setFlags(["-no-remote", "about:"])
            elif args[1] == "-no-remote":
                self._firefox.setFlags(["-no-remote", "about:"])
            elif args[1] == "-reset":
                self._reset()
                raise SystemExit(0)
            else:
                raise SystemExit(sys.argv[0] + ': Invalid "' + args[1] + '" option.')
            args.remove(args[1])

        # Avoids "exo-helper-1 firefox http://" problem of clicking text in XFCE
        if len(args) > 1:
            ppid = os.getppid()
            if ppid != 1 and "exo-helper" in syslib.Task().getProcess(ppid)["COMMAND"]:
                raise SystemExit

        self._firefox.setArgs(args[1:])
        self._filter = (
            "^$|Failed to load module|: G[dt]k-WARNING |: G[dt]k-CRITICAL |:"
            " GLib-GObject-|: GnomeUI-WARNING|^OpenGL Warning: | Pango-WARNING |"
            "^WARNING: Application calling GLX |: libgnomevfs-WARNING |: wrong ELF class|"
            "(child|parent) won, so we|processing deferred in-call|is not defined|"
            "^failed to create drawable|None of the authentication protocols|"
            "NOTE: child process received|: Not a directory|[/ ]thumbnails |"
            ": Connection reset by peer|")
        self._config()
        self._prefs(updates)

    def getFilter(self):
        """
        Return filter patern.
        """
        return self._filter

    def getFirefox(self):
        """
        Return Firefox Command class object.
        """
        return self._firefox

    def _config(self):
        if "HOME" in os.environ:
            adobe = os.path.join(os.environ["HOME"], ".adobe", "Flash_Player", "AssetCache")
            macromedia = os.path.join(os.environ["HOME"], ".macromedia",
                                      "Flash_Player", "macromedia.com")
            if not os.path.isfile(adobe) or not os.path.isfile(macromedia):
                try:
                    shutil.rmtree(os.path.join(os.environ["HOME"], ".adobe"))
                    os.makedirs(os.path.dirname(adobe))
                    with open(adobe, "w", newline="\n") as ofile:
                        pass
                    shutil.rmtree(os.path.join(os.environ["HOME"], ".macromedia"))
                    os.makedirs(os.path.dirname(macromedia))
                    with open(macromedia, "w", newline="\n") as ofile:
                        pass
                except OSError:
                    pass
            try:
                shutil.rmtree(os.path.join(os.path.dirname(macromedia), "#SharedObjects"))
            except OSError:
                pass

            firefoxdir = os.path.join(os.environ["HOME"], ".mozilla", "firefox")
            if os.path.isdir(firefoxdir):
                os.chmod(firefoxdir, int("700", 8))
                # Remove old session data and lock file (allows multiple instances)
                for file in (glob.glob(os.path.join(firefoxdir, "*", "sessionstore.js")) +
                             glob.glob(os.path.join(firefoxdir, "*", ".parentlock")) +
                             glob.glob(os.path.join(firefoxdir, "*", "lock")) +
                             glob.glob(os.path.join(firefoxdir, "*", "*.log"))):
                    try:
                        os.remove(file)
                    except OSError:
                        continue
                ispattern = re.compile("^(lastDownload|lastSuccess|lastCheck|expires|"
                                       "softExpiration)=\d*")
                for file in glob.glob(os.path.join(firefoxdir, "*", "adblockplus", "patterns.ini")):
                    try:
                        with open(file, errors="replace") as ifile:
                            with open(file + "-new", "w", newline="\n") as ofile:
                                for line in ifile:
                                    if not ispattern.search(line):
                                        print(line, end="", file=ofile)
                    except IOError:
                        try:
                            os.remove(file + "-new")
                        except OSError:
                            continue
                    else:
                        try:
                            os.rename(file + "-new", file)
                        except OSError:
                            continue

                for directory in glob.glob(os.path.join(firefoxdir, "*")):
                    file = os.path.join(directory, "xulstore.json")
                    try:
                        with open(file) as ifile:
                            with open(file + "-new", "w", newline="\n") as ofile:
                                for line in ifile:
                                    print(line.replace('"fullscreen"', '"maximized"'),
                                          end="", file=ofile)
                    except IOError:
                        try:
                            os.remove(file + "-new")
                        except OSError:
                            pass
                    else:
                        try:
                            os.rename(file + "-new", file)
                        except OSError:
                            pass

            if os.path.isfile(self._firefox.getFile() + "-bin"):
                setmod = syslib.Command("setmod", check=False)
                if setmod.isFound():
                    # Fix permissions if owner and updated
                    setmod.setArgs(["wa", os.path.dirname(self._firefox.getFile())])
                    setmod.run(mode="daemon")

    def _copy(self):
        if "HOME" in os.environ:
            task = syslib.Task()
            for directory in glob.glob(os.path.join("/tmp",
                                       "firefox-" + syslib.info.getUsername() + ".*")):
                try:
                    if not task.pgid2pids(int(directory.split(".")[-1])):
                        print('Removing copy of Firefox profile in "' + directory + '"...')
                        try:
                            shutil.rmtree(directory)
                        except OSError:
                            pass
                except ValueError:
                    pass

            os.umask(int("077", 8))
            firefoxdir = os.path.join(os.environ["HOME"], ".mozilla", "firefox")
            mypid = os.getpid()
            os.setpgid(mypid, mypid)  # New PGID
            newhome = os.path.join(
                "/tmp", "firefox-" + syslib.info.getUsername() + "." + str(mypid))
            os.environ["TMPDIR"] = newhome
            print('Creating copy of Firefox profile in "' + newhome + '"...')

            if not os.path.isdir(newhome):
                try:
                    shutil.copytree(firefoxdir, os.path.join(newhome, ".mozilla", "firefox"))
                except (IOError, shutil.Error):  # Ignore "lock" file error
                    pass
            for directory in ("Desktop", ".cups"):
                try:
                    os.symlink(os.path.join(os.environ["HOME"], directory),
                               os.path.join(newhome, directory))
                except OSError:
                    pass
            os.environ["HOME"] = newhome

    def _reset(self):
        if "HOME" in os.environ:
            firefoxdir = os.path.join(os.environ["HOME"], ".mozilla", "firefox")
            if os.path.isdir(firefoxdir):
                keepList = ("adblockplus", "extensions", "extension-data", "extensions.json",
                            "extensions.sqlite", "localstore.rdf", "mimeTypes.rdf",
                            "permissions.sqlite", "prefs.js", "user.js", "xulstore.json")
                for directory in glob.glob(os.path.join(firefoxdir, "*")):
                    if os.path.isfile(os.path.join(directory, "prefs.js")):
                        for file in (glob.glob(os.path.join(directory, ".*")) +
                                     glob.glob(os.path.join(directory, "*"))):
                            if os.path.basename(file) not in keepList:
                                print('Removing "{0:s}"...'.format(file))
                                try:
                                    if os.path.isdir(file):
                                        shutil.rmtree(file)
                                    else:
                                        os.remove(file)
                                except OSError:
                                    continue
                        for file in glob.glob(os.path.join(directory, "adblockplus",
                                                           "patterns-backup*ini")):
                            try:
                                os.remove(file)
                            except OSError:
                                pass

    def _prefs(self, updates):
        if "HOME" in os.environ:
            firefoxdir = os.path.join(os.environ["HOME"], ".mozilla", "firefox")
            if os.path.isdir(firefoxdir):
                for file in glob.glob(os.path.join(firefoxdir, "*", "prefs.js")):
                    try:
                        with open(file, errors="replace") as ifile:
                            lines = ifile.readlines()
                        # Workaround "user.js" dropped support
                        with open(file, "a", newline="\n") as ofile:
                            if (not updates and
                                    'user_pref("app.update.enabled", false);\n' not in lines):
                                print('user_pref("app.update.enabled", false);', file=ofile)
                            for setting in ('"extensions.blocklist.enabled", false',
                                            '"full-screen-api.approval-required", false',
                                            '"layout.spellcheckDefault", 2',
                                            '"media.autoplay.enabled", false',
                                            '"media.fragmented-mp4.exposed", true',
                                            '"media.fragmented-mp4.ffmpeg.enabled", true',
                                            '"media.fragmented-mp4.gmp.enabled", true',
                                            '"media.gstreamer.enabled", false',
                                            '"media.mediasource.enabled", true',
                                            '"media.mediasource.mp4.enabled", true',
                                            '"media.mediasource.webm.enabled", true',
                                            '"plugins.click_to_play", true'):
                                if 'user_pref(' + setting + ');\n' not in lines:
                                    print('user_pref(' + setting + ');', file=ofile)
                    except IOError:
                        pass


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getFirefox().run(filter=options.getFilter(), mode="background")
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
