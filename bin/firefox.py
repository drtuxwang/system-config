#!/usr/bin/env python3
"""
Wrapper for 'firefox' command

Use '-copy' to copy profile to '/tmp' and use '-no-remote about:'
Use '-no-remote' to avoid using current instance
Use '-reset' to clean junk from profile
"""

import getpass
import glob
import os
import re
import shutil
import signal
import sqlite3
import sys

import command_mod
import subtask_mod
import task_mod

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pattern(self):
        """
        Return filter patern.
        """
        return self._pattern

    def get_firefox(self):
        """
        Return Firefox Command class object.
        """
        return self._firefox

    @staticmethod
    def _clean_adobe():
        adobe = os.path.join(os.environ['HOME'], '.adobe', 'Flash_Player', 'AssetCache')
        macromedia = os.path.join(os.environ['HOME'], '.macromedia',
                                  'Flash_Player', 'macromedia.com')
        if not os.path.isfile(adobe) or not os.path.isfile(macromedia):
            try:
                shutil.rmtree(os.path.join(os.environ['HOME'], '.adobe'))
                os.makedirs(os.path.dirname(adobe))
                with open(adobe, 'w', newline='\n'):
                    pass
                shutil.rmtree(os.path.join(os.environ['HOME'], '.macromedia'))
                os.makedirs(os.path.dirname(macromedia))
                with open(macromedia, 'w', newline='\n'):
                    pass
            except OSError:
                pass
        try:
            shutil.rmtree(os.path.join(os.path.dirname(macromedia), '#SharedObjects'))
        except OSError:
            pass

    @staticmethod
    def _remove_lock(firefoxdir):
        # Remove old session data and lock file (allows multiple instances)
        for file in (glob.glob(os.path.join(firefoxdir, '*', 'sessionstore.js')) +
                     glob.glob(os.path.join(firefoxdir, '*', '.parentlock')) +
                     glob.glob(os.path.join(firefoxdir, '*', 'lock')) +
                     glob.glob(os.path.join(firefoxdir, '*', '*.log'))):
            try:
                os.remove(file)
            except OSError:
                continue

    @staticmethod
    def _remove_junk_files(firefoxdir):
        ispattern = re.compile(
            r'^(lastDownload|lastSuccess|lastCheck|expires|softExpiration)=\d*')
        for file in glob.glob(os.path.join(firefoxdir, '*', 'adblockplus', 'patterns.ini')):
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

    @staticmethod
    def _fix_xulstore(firefoxdir):
        for directory in glob.glob(os.path.join(firefoxdir, '*')):
            file = os.path.join(directory, 'xulstore.json')
            try:
                with open(file) as ifile:
                    with open(file + '-new', 'w', newline='\n') as ofile:
                        for line in ifile:
                            print(line.replace('"fullscreen"', '"maximized"'),
                                  end='', file=ofile)
            except OSError:
                try:
                    os.remove(file + '-new')
                except OSError:
                    pass
            else:
                try:
                    shutil.move(file + '-new', file)
                except OSError:
                    pass

    def _fix_permissions(self):
        if os.path.isfile(self._firefox.get_file() + '-bin'):
            fmod = command_mod.Command('fmod', errors='ignore')
            if fmod.is_found():
                # Fix permissions if owner and updated
                fmod.set_args(['wa', os.path.dirname(self._firefox.get_file())])
                subtask_mod.Daemon(fmod.get_cmdline()).run()

    def _config(self):
        self._clean_adobe()

        firefoxdir = os.path.join(os.environ['HOME'], '.mozilla', 'firefox')
        if os.path.isdir(firefoxdir):
            os.chmod(firefoxdir, int('700', 8))
            self._remove_lock(firefoxdir)
            self._remove_junk_files(firefoxdir)
            self._fix_xulstore(firefoxdir)

        self._fix_permissions()

    @staticmethod
    def _copy():
        if 'HOME' in os.environ:
            task = task_mod.Tasks.factory()
            for directory in glob.glob(
                    os.path.join('/tmp', 'firefox-' + getpass.getuser() + '.*')):
                try:
                    if not task.pgid2pids(int(directory.split('.')[-1])):
                        print('Removing copy of Firefox profile in "' + directory + '"...')
                        try:
                            shutil.rmtree(directory)
                        except OSError:
                            pass
                except ValueError:
                    pass

            os.umask(int('077', 8))
            firefoxdir = os.path.join(os.environ['HOME'], '.mozilla', 'firefox')
            mypid = os.getpid()
            os.setpgid(mypid, mypid)  # New PGID
            newhome = os.path.join('/tmp', 'firefox-' + getpass.getuser() + '.' + str(mypid))
            os.environ['TMPDIR'] = newhome
            print('Creating copy of Firefox profile in "' + newhome + '"...')

            if not os.path.isdir(newhome):
                try:
                    shutil.copytree(firefoxdir, os.path.join(newhome, '.mozilla', 'firefox'))
                except (OSError, shutil.Error):  # Ignore 'lock' file error
                    pass
            for directory in ('Desktop', '.cups'):
                try:
                    os.symlink(os.path.join(os.environ['HOME'], directory),
                               os.path.join(newhome, directory))
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
        if 'HOME' not in os.environ:
            return

        firefoxdir = os.path.join(os.environ['HOME'], '.mozilla', 'firefox')
        if os.path.isdir(firefoxdir):
            keep_list = ('adblockplus', 'extensions', 'extension-data', 'extensions.json',
                         'extensions.sqlite', 'localstore.rdf', 'mimeTypes.rdf',
                         'permissions.sqlite', 'prefs.js', 'user.js', 'xulstore.json')
            for directory in glob.glob(os.path.join(firefoxdir, '*')):
                if os.path.isfile(os.path.join(directory, 'prefs.js')):
                    for file in (glob.glob(os.path.join(directory, '.*')) +
                                 glob.glob(os.path.join(directory, '*'))):
                        if os.path.basename(file) not in keep_list:
                            print('Removing "{0:s}"...'.format(file))
                            self._remove(file)
                    for file in glob.glob(os.path.join(
                            directory, 'adblockplus', 'patterns-backup*ini')):
                        self._remove(file)

    @staticmethod
    def _prefs(updates):
        firefoxdir = os.path.join(os.environ['HOME'], '.mozilla', 'firefox')
        if os.path.isdir(firefoxdir):
            for file in glob.glob(os.path.join(firefoxdir, '*', 'prefs.js')):
                try:
                    with open(file, errors='replace') as ifile:
                        lines = ifile.readlines()
                    # Workaround 'user.js' dropped support
                    with open(file, 'a', newline='\n') as ofile:
                        if (not updates and
                                'user_pref("app.update.enabled", false);\n' not in lines):
                            print('user_pref("app.update.enabled", false);', file=ofile)
                        for setting in ('"accessibility.typeaheadfind.enablesound", false',
                                        '"browser.blink_allowed", false',
                                        '"browser.bookmarks.max_backups", 1',
                                        '"browser.safebrowsing.enabled", false',
                                        '"browser.safebrowsing.malware.enabled", false',
                                        '"browser.cache.memory.capacity", 16384',
                                        '"browser.display.show_image_placeholders", false',
                                        '"browser.download.animateNotifications", false',
                                        '"browser.link.open_external", 3',
                                        '"browser.link.open_newwindow", 3',
                                        '"browser.link.open_newwindow.restriction", 0',
                                        '"browser.newtabpage.enabled", false',
                                        '"browser.pocket.enabled", false',
                                        '"browser.tabs.animate", false',
                                        '"browser.tabs.insertRelatedAfterCurrent", false',
                                        '"browser.urlbar.autoFill", false',
                                        '"browser.sessionhistory.max_total_viewers", 0',
                                        '"browser.sessionhistory.max_viewers", 0',
                                        '"browser.sessionhistory.sessionhistory.max_entries", 5',
                                        '"browser.sessionstore.resume_from_crash", false',
                                        '"browser.sessionstore.max_resumed_crashes", 0',
                                        '"browser.sessionstore.max_tabs_undo", 0',
                                        '"browser.shell.checkDefaultBrowser", false',
                                        '"browser.zoom.siteSpecific", false',
                                        '"content.interrupt.parsing", true',
                                        '"content.notify.backoffcount", 5',
                                        '"content.notify.interval", 500000',
                                        '"content.notify.ontimer", true',
                                        '"dom.event.contextmenu.enabled", false',
                                        '"dom.max_script_run_time", 20',
                                        '"dom.push.enable", false',
                                        '"extensions.blocklist.enabled", false',
                                        '"full-screen-api.approval-required", false',
                                        '"geo.enabled", false',
                                        '"image.animation_mode", "none"',
                                        '"keyword.enabled", true',
                                        '"layout.frames.force_resizability", true',
                                        '"layout.spellcheckDefault", 2',
                                        '"loop.throttled", false',
                                        '"media.autoplay.enabled", false',
                                        '"media.fragmented-mp4.exposed", true',
                                        '"media.fragmented-mp4.ffmpeg.enabled", true',
                                        '"media.fragmented-mp4.gmp.enabled", false',
                                        '"media.gstreamer.enabled", false',
                                        '"media.mediasource.enabled", true',
                                        '"media.mediasource.mp4.enabled", true',
                                        '"media.mediasource.webm.enabled", true',
                                        '"network.http.pipelining.maxrequests", 8',
                                        '"network.http.pipelining", true',
                                        '"network.http.proxy.pipelining", true',
                                        '"network.http.spdy.enabled", true',
                                        '"network.prefetch-next", false',
                                        '"nglayout.initialpaint.delay", 0',
                                        '"print.print_edge_bottom", 20',
                                        '"print.print_edge_left", 20',
                                        '"print.print_edge_right", 20',
                                        '"print.print_edge_top", 20',
                                        '"plugins.click_to_play", true',
                                        '"reader.parse-on-load.enabled", false',
                                        '"security.dialog_enable_delay", 0',
                                        '"toolkit.telemetry.enabled", false',
                                        '"toolkit.storage.synchronous", 0',
                                        '"ui.submenuDelay", 0'):
                            if 'user_pref(' + setting + ');\n' not in lines:
                                print('user_pref(' + setting + ');', file=ofile)
                except OSError:
                    pass

    @staticmethod
    def _ublock():
        firefoxdir = os.path.join(os.environ['HOME'], '.mozilla', 'firefox')
        for file in glob.glob(os.path.join(firefoxdir, '*', 'extension-data', 'ublock0.sqlite')):
            if os.path.isfile(file):
                with sqlite3.connect(file) as conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                             "UPDATE settings SET value = '{}' WHERE name = 'cached_asset_entries'")
                        cursor.execute("DELETE FROM settings WHERE name = 'selfie'")
                    except sqlite3.DatabaseError:
                        pass

    def parse(self, args):
        """
        Parse arguments
        """
        self._firefox = command_mod.Command(
            os.path.basename(args[0]).replace('.py', ''), errors='stop')
        updates = os.access(self._firefox.get_file(), os.W_OK)

        while len(args) > 1:
            if not args[1].startswith('-'):
                break
            elif args[1] in ('-copy', '-no-remote'):
                if args[1] == '-copy':
                    updates = False
                    self._copy()
                self._firefox.set_args(['-no-remote'])
                if 'about:' not in args:
                    self._firefox.append_arg('about:')
            elif args[1] == '-reset':
                self._reset()
                raise SystemExit(0)
            else:
                raise SystemExit(sys.argv[0] + ': Invalid "' + args[1] + '" option.')
            args.remove(args[1])

        # Avoids 'exo-helper-1 firefox http://' problem of clicking text in XFCE
        if len(args) > 1:
            ppid = os.getppid()
            if ppid != 1 and 'exo-helper' in task_mod.Tasks.factory().get_process(ppid)['COMMAND']:
                raise SystemExit

        self._firefox.extend_args(args[1:])
        self._pattern = (
            '^$|Failed to load module|: G[dt]k-WARNING |: G[dt]k-CRITICAL |:'
            ' GLib-GObject-|: GnomeUI-WARNING|^OpenGL Warning: | Pango-WARNING |'
            '^WARNING: Application calling GLX |: libgnomevfs-WARNING |: wrong ELF class|'
            '(child|parent) won, so we|processing deferred in-call|is not defined|'
            '^failed to create drawable|None of the authentication protocols|'
            'NOTE: child process received|: Not a directory|[/ ]thumbnails |'
            ': Connection reset by peer|')

        if 'HOME' in os.environ:
            self._config()
            self._prefs(updates)
            self._ublock()


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

        subtask_mod.Background(
            options.get_firefox().get_cmdline()).run(pattern=options.get_pattern())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
