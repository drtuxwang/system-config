#!/usr/bin/env python3
"""
Wrapper for 'chromium-browser' and 'chromium' command

Use '-copy' to copy profile to '/tmp'
Use '-reset' to clean junk from profile
Use '-restart' to restart chrome
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import json
import os
import re
import shutil
import signal

import syslib


class Options:

    def __init__(self, args):
        self._chrome = syslib.Command('chromium-browser', check=False)
        self._directory = 'chromium'
        if not self._chrome.isFound():
            self._chrome = syslib.Command('chromium')

        if len(args) > 1:
            if args[1] == '-version':
                self._chrome.setArgs(['-version'])
                self._chrome.run(mode='exec')
            elif args[1] == '-copy':
                self._copy()
            elif args[1] == '-reset':
                self._reset()
                raise SystemExit(0)

            if args[1] == '-restart':
                self._restart()
                args = args[1:]
            self._chrome.setArgs(args[1:])

        # Avoids 'exo-helper-1 chromium http://' problem of clicking text in XFCE
        if len(args) > 1:
            ppid = os.getppid()
            if ppid != 1 and 'exo-helper' in syslib.Task().getProcess(ppid)['COMMAND']:
                raise SystemExit

        if '--disable-background-mode' not in self._chrome.getArgs():
            self._chrome.extendFlags(['--disable-background-mode', '--disable-geolocation',
                                      '--disk-cache-size=0'])

        # Get flash player
        if '--ppapi-flash-path=' not in ''.join(self._chrome.getArgs()):
            flashPlayer = FlashPlayer(self._chrome)
            if flashPlayer.getVersion():
                self._chrome.extendFlags(['--ppapi-flash-path=' + flashPlayer.getPlugin(),
                                          '--ppapi-flash-version=' + flashPlayer.getVersion()])

        # Suid sandbox workaround
        if 'HOME' in os.environ:
            if syslib.FileStat(os.path.join(os.path.dirname(self._chrome.getFile()),
                               'chrome-sandbox')).getMode() != 104755:
                self._chrome.extendFlags(['--test-type', '--disable-setuid-sandbox'])

        self._filter = ('^$|^NPP_GetValue|NSS_VersionCheck| Gtk:|: GLib-GObject-CRITICAL|'
                        ' GLib-GObject:|: no version information available|:ERROR:.*[.]cc|'
                        'Running without renderer sandbox|:Gdk-WARNING |: DEBUG: |^argv|')
        self._config(args)
        self._setLibraries(self._chrome)

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getChrome(self):
        """
        Return chrome Command class object.
        """
        return self._chrome

    def _config(self, args):
        if 'HOME' in os.environ:
            adobe = os.path.join(os.environ['HOME'], '.adobe', 'Flash_Player', 'AssetCache')
            macromedia = os.path.join(os.environ['HOME'], '.macromedia',
                                      'Flash_Player', 'macromedia.com')
            if not os.path.isfile(adobe) or not os.path.isfile(macromedia):
                try:
                    shutil.rmtree(os.path.join(os.environ['HOME'], '.adobe'))
                    os.makedirs(os.path.dirname(adobe))
                    with open(adobe, 'w', newline='\n') as ofile:
                        pass
                    shutil.rmtree(os.path.join(os.environ['HOME'], '.macromedia'))
                    os.makedirs(os.path.dirname(macromedia))
                    with open(macromedia, 'w', newline='\n') as ofile:
                        pass
                except OSError:
                    pass
            try:
                shutil.rmtree(os.path.join(os.path.dirname(macromedia), '#SharedObjects'))
            except OSError:
                pass

            configdir = os.path.join(os.environ['HOME'], '.config', self._directory, 'Default')

            file = os.path.join(configdir, 'Preferences')
            try:
                with open(file) as ifile:
                    data = json.load(ifile)
                data['profile']['exit_type'] = 'Normal'
                data['profile']['per_host_zoom_levels'] = {}
                with open(file + '-new', 'w', newline='\n') as ofile:
                    print(json.dumps(data, indent=4, sort_keys=True), file=ofile)
            except (IOError, KeyError, ValueError):
                try:
                    os.remove(file + '-new')
                except OSError:
                    pass
            else:
                try:
                    os.rename(file + '-new', file)
                except OSError:
                    pass

            if os.path.isdir(configdir):
                for fileglob in ('Archive*', 'Cookies*', 'Current*', 'History*',
                                 'Last*', 'Visited*', 'Last*'):
                    for file in glob.glob(os.path.join(configdir, fileglob)):
                        try:
                            os.remove(file)
                        except OSError:
                            pass
                ispattern = re.compile('^(lastDownload|lastSuccess|lastCheck|'
                                       'expires|softExpiration)=\d*')
                for file in glob.glob(os.path.join(configdir, 'File System', '*', 'p', '00', '*')):
                    try:
                        with open(file, errors='replace') as ifile:
                            with open(file + '-new', 'w', newline='\n') as ofile:
                                for line in ifile:
                                    if not ispattern.search(line):
                                        print(line, end='', file=ofile)
                    except IOError:
                        try:
                            os.remove(file + '-new')
                        except OSError:
                            continue
                    else:
                        try:
                            os.rename(file + '-new', file)
                        except OSError:
                            continue

            for file in (os.path.join(os.environ['HOME'], '.cache', self._directory),
                         os.path.join(configdir, 'Pepper Data')):
                if not os.path.isfile(file):
                    try:
                        if os.path.isdir(file):
                            shutil.rmtree(file)
                        with open(file, 'wb'):
                            pass
                    except (IOError, OSError):
                        pass

    def _copy(self):
        if 'HOME' in os.environ:
            task = syslib.Task()
            for directory in glob.glob(
                    os.path.join('/tmp', 'chrome-' + syslib.info.getUsername() + '.*')):
                try:
                    if not task.pgid2pids(int(directory.split('.')[-1])):
                        print('Removing copy of Chrome profile in "' + directory + '"...')
                        try:
                            shutil.rmtree(directory)
                        except OSError:
                            pass
                except ValueError:
                    pass
            os.umask(int('077', 8))
            configdir = os.path.join(os.environ['HOME'], '.config', self._directory)
            mypid = os.getpid()
            os.setpgid(mypid, mypid)  # New PGID
            newhome = os.path.join('/tmp', 'chrome-' + syslib.info.getUsername() + '.' + str(mypid))
            print('Creating copy of Chrome profile in "' + newhome + '"...')
            if not os.path.isdir(newhome):
                try:
                    shutil.copytree(configdir, os.path.join(newhome, '.config', self._directory))
                except (IOError, shutil.Error):  # Ignore 'lock' file error
                    pass
            try:
                os.symlink(os.path.join(os.environ['HOME'], 'Desktop'),
                           os.path.join(newhome, 'Desktop'))
            except OSError:
                pass
            os.environ['HOME'] = newhome

    def _reset(self):
        if 'HOME' in os.environ:
            configdir = os.path.join(os.environ['HOME'], '.config', self._directory)
            if os.path.isdir(configdir):
                keepList = ('Extensions', 'File System', 'Local Extension Settings',
                            'Local Storage', 'Preferences', 'Secure Preferences')
                for directory in glob.glob(os.path.join(configdir, '*')):
                    if os.path.isfile(os.path.join(directory, 'Preferences')):
                        for file in glob.glob(os.path.join(directory, '*')):
                            if os.path.basename(file) not in keepList:
                                print('Removing "{0:s}"...'.format(file))
                                try:
                                    if os.path.isdir(file):
                                        shutil.rmtree(file)
                                    else:
                                        os.remove(file)
                                except OSError:
                                    continue
                    elif os.path.basename(directory) not in ('First Run', 'Local State'):
                        print('Removing "{0:s}"...'.format(directory))
                        try:
                            if os.path.isdir(directory):
                                shutil.rmtree(directory)
                            else:
                                os.remove(directory)
                        except OSError:
                            continue

    def _restart(self):
        if 'HOME' in os.environ:
            configdir = os.path.join(os.environ['HOME'], '.config', 'google-chrome')
            try:
                pid = os.readlink(os.path.join(configdir, 'SingletonLock')).split('-')[1]
                syslib.Task().killpids([pid])
            except (IndexError, OSError):
                pass

    def _setLibraries(self, command):
        libdir = os.path.join(os.path.dirname(command.getFile()), 'lib')
        if os.path.isdir(libdir):
            if syslib.info.getSystem() == 'linux':
                if not os.path.isfile('/usr/lib/libnss3.so.1d'):  # use workaround
                    if 'LD_LIBRARY_PATH' in os.environ:
                        os.environ['LD_LIBRARY_PATH'] = (
                            libdir + os.pathsep + os.environ['LD_LIBRARY_PATH'])
                    else:
                        os.environ['LD_LIBRARY_PATH'] = libdir


class FlashPlayer:

    def __init__(self, chrome):
        self._plugin = None
        self._version = None

        file = os.path.join(os.path.dirname(
            chrome.getFile()), 'PepperFlash', 'libpepflashplayer.so')
        if os.path.isfile(file):
            self._detect(file)

        setflash = syslib.Command('setflash', check=False)
        if setflash.isFound():
            setflash.run(mode='batch')
            if setflash.hasOutput():
                self._detect(setflash.getOutput()[0])

    def getPlugin(self):
        """
        Return plugin location.
        """
        return self._plugin

    def getVersion(self):
        """
        Return version of files.
        """
        return self._version

    def _detect(self, file):
        self._plugin = file
        try:
            with open(os.path.join(os.path.dirname(file), 'manifest.json'),
                      errors='replace') as ifile:
                for line in ifile:
                    if 'version' in line:
                        try:
                            self._version = line.split('"')[3]
                            return
                        except IndexError:
                            break
        except IOError:
            pass
        self._version = '0.0.0.0'


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getChrome().run(filter=options.getFilter(), mode='background')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
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


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
