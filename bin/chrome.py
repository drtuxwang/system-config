#!/usr/bin/env python3
"""
Wrapper for "google-chrome" commands

Use '-copy' to copy profile to '/tmp'
Use '-reset' to clean junk from profile
Use '-restart' to restart chrome
"""

import getpass
import glob
import json
import os
import re
import shutil
import signal
import sys
import time

import command_mod
import subtask_mod
import task_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pattern(self):
        """
        Return filter pattern.
        """
        return self._pattern

    def get_chrome(self):
        """
        Return chrome Command class object.
        """
        return self._chrome

    @staticmethod
    def _get_profiles_dir():
        if command_mod.Platform.get_system() == 'macos':
            return os.path.join(
                'Library', 'Application Support', 'Google', 'Chrome')
        return os.path.join('.config', 'google-chrome')

    @staticmethod
    def _clean_adobe():
        adobe = os.path.join(
            os.environ['HOME'], '.adobe', 'Flash_Player', 'AssetCache')
        macromedia = os.path.join(
            os.environ['HOME'],
            '.macromedia',
            'Flash_Player',
            'macromedia.com'
        )
        if not os.path.isfile(adobe) or not os.path.isfile(macromedia):
            try:
                shutil.rmtree(os.path.join(os.environ['HOME'], '.adobe'))
                os.makedirs(os.path.dirname(adobe))
                with open(adobe, 'w', newline='\n'):
                    pass
                shutil.rmtree(
                    os.path.join(os.environ['HOME'], '.macromedia'))
                os.makedirs(os.path.dirname(macromedia))
                with open(macromedia, 'w', newline='\n'):
                    pass
            except OSError:
                pass
        try:
            shutil.rmtree(
                os.path.join(os.path.dirname(macromedia), '#SharedObjects'))
        except OSError:
            pass

        file = os.path.join(os.environ['HOME'], '.cache', 'google-chrome')
        if not os.path.isfile(file):
            try:
                if os.path.isdir(file):
                    shutil.rmtree(file)
                with open(file, 'wb'):
                    pass
            except OSError:
                pass

    @staticmethod
    def _clean_preferences(configdir):
        file = os.path.join(configdir, 'Preferences')
        try:
            with open(file) as ifile:
                data = json.load(ifile)
            data['profile']['exit_type'] = 'Normal'
            data['partition']['per_host_zoom_levels'] = {}
            with open(file + '-new', 'w', newline='\n') as ofile:
                print(json.dumps(data, indent=4, sort_keys=True), file=ofile)
        except (KeyError, OSError, ValueError):
            try:
                os.remove(file + '-new')
            except OSError:
                pass
        else:
            try:
                shutil.move(file + '-new', file)
            except OSError:
                pass

    @staticmethod
    def _clean_junk_files(configdir):
        for fileglob in ('Archive*', 'Cookies*', 'Current*', 'History*',
                         'Last*', 'Visited*', 'Last*'):
            for file in glob.glob(os.path.join(configdir, fileglob)):
                try:
                    os.remove(file)
                except OSError:
                    pass
        ispattern = re.compile('^(lastDownload|lastSuccess|lastCheck|'
                               r'expires|softExpiration)=\d*')
        for file in glob.glob(
                os.path.join(configdir, 'File System', '*', 'p', '00', '*')):
            try:
                with open(file, errors='replace') as ifile:
                    with open(file + '-new', 'w', newline='\n') as ofile:
                        for line in ifile:
                            if not ispattern.search(line):
                                print(line, end='', file=ofile)
            except OSError:
                try:
                    os.remove(file + '-new')
                except OSError:
                    continue
            else:
                try:
                    shutil.move(file + '-new', file)
                except OSError:
                    continue

    def _config(self):
        home = os.environ.get('HOME', '')
        configdir = os.path.join(home, self._get_profiles_dir(), 'Default')

        self._clean_adobe()
        if os.path.isdir(configdir):
            self._clean_preferences(configdir)
            self._clean_junk_files(configdir)

    def _copy(self):
        task = task_mod.Tasks.factory()
        for directory in glob.glob(os.path.join(
                '/tmp',
                'chrome-' + getpass.getuser() + '.*'
        )):
            try:
                if not task.pgid2pids(int(directory.split('.')[-1])):
                    print(
                        'Removing copy of Chrome profile in "' +
                        directory + '"...'
                    )
                    try:
                        shutil.rmtree(directory)
                    except OSError:
                        pass
            except ValueError:
                pass
        os.umask(int('077', 8))
        configdir = os.path.join(
            os.environ['HOME'],
            self._get_profiles_dir()
        )
        mypid = os.getpid()
        os.setpgid(mypid, mypid)  # New PGID
        newhome = os.path.join(
            '/tmp',
            'chrome-' + getpass.getuser() + '.' + str(mypid)
        )
        print('Creating copy of Chrome profile in "' + newhome + '"...')
        if not os.path.isdir(newhome):
            try:
                shutil.copytree(
                    configdir,
                    os.path.join(newhome, self._get_profiles_dir())
                )
            except (OSError, shutil.Error):  # Ignore 'lock' file error
                pass
        try:
            os.symlink(
                os.path.join(os.environ.get('HOME', ''), 'Desktop'),
                os.path.join(newhome, 'Desktop')
            )
        except OSError:
            pass
        os.environ['HOME'] = newhome

    @staticmethod
    def _remove(file):
        try:
            if os.path.isdir(file):
                shutil.rmtree(file)
            else:
                os.remove(file)
        except OSError:
            pass

    def _reset(self):
        home = os.environ.get('HOME', '')
        configdir = os.path.join(home, self._get_profiles_dir())
        if os.path.isdir(configdir):
            keep_list = (
                'Extensions',
                'File System',
                'Local Extension Settings',
                'Local Storage',
                'Preferences',
                'Secure Preferences'
            )
            for directory in glob.glob(os.path.join(configdir, '*')):
                if os.path.isfile(os.path.join(directory, 'Preferences')):
                    for file in glob.glob(os.path.join(directory, '*')):
                        if os.path.basename(file) not in keep_list:
                            print('Removing "{0:s}"...'.format(file))
                            self._remove(file)
                elif (
                        os.path.basename(directory) not in
                        {'First Run', 'Local State'}
                ):
                    print('Removing "{0:s}"...'.format(directory))
                    self._remove(directory)
                for file in glob.glob(os.path.join(
                        directory, 'Local Storage', 'https*')):
                    self._remove(file)

    def _restart(self):
        home = os.environ.get('HOME', '')
        configdir = os.path.join(home, self._get_profiles_dir())
        try:
            pid = os.readlink(
                os.path.join(configdir, 'SingletonLock')).split('-')[1]
            task_mod.Tasks.factory().killpids([pid])
        except (IndexError, OSError):
            pass

    @staticmethod
    def _set_libraries(command):
        libdir = os.path.join(os.path.dirname(command.get_file()), 'lib')
        if os.path.isdir(libdir) and os.name == 'posix':
            if os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        libdir + os.pathsep + os.environ['LD_LIBRARY_PATH'])
                else:
                    os.environ['LD_LIBRARY_PATH'] = libdir

    @staticmethod
    def _locate():
        commands = ['google-chrome']
        for command in commands:
            chrome = command_mod.Command(command, errors='ignore')
            if chrome.is_found():
                return chrome
        return command_mod.Command('chrome', errors='stop')

    def parse(self, args):
        """
        Parse arguments
        """
        self._chrome = self._locate()

        if len(args) > 1:
            if args[1] == '-version':
                self._chrome.set_args(['-version'])
                subtask_mod.Exec(self._chrome.get_cmdline()).run()
            elif args[1] == '-copy':
                self._copy()
            elif args[1] == '-reset':
                self._reset()
                raise SystemExit(0)

            if args[1] == '-restart':
                self._restart()
                args = args[1:]
            self._chrome.set_args(args[1:])

        # Avoids 'exo-helper-1 chrome http://' problem of clicking text in XFCE
        if len(args) > 1:
            ppid = os.getppid()
            if (ppid != 1 and
                    'exo-helper' in
                    task_mod.Tasks.factory().get_process(ppid)['COMMAND']):
                raise SystemExit

        if '--disable-background-mode' not in self._chrome.get_args():
            self._chrome.extend_args([
                '--disable-background-mode',
                '--disable-geolocation',
                '--disable-infobars',
                '--disk-cache-dir=/dev/null',
                '--disk-cache-size=1',
                '--process-per-site',
                '--site-per-process',
            ])

        # No sandbox workaround
        if not os.path.isfile('/usr/lib/chromium-browser/chrome-sandbox'):
            self._chrome.append_arg('--no-sandbox')

        self._pattern = (
            '^$|^NPP_GetValue|NSS_VersionCheck| Gtk:|: GLib-GObject-CRITICAL|'
            ' GLib-GObject:|: no version information available|:ERROR:.*[.]cc|'
            'Running without renderer sandbox|:Gdk-WARNING |: DEBUG: |^argv|'
        )
        self._config()
        self._set_libraries(self._chrome)


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        subtask_mod.Background(options.get_chrome().get_cmdline()).run(
            pattern=options.get_pattern())

        # Kill filtering process after start up to avoid hang
        time.sleep(1)
        task = task_mod.Tasks.factory()
        task.killpids(task.get_child_pids(os.getpid()))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
