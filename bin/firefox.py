#!/usr/bin/env python3
"""
Wrapper for "firefox" command

Use '-reset' to clean junk from profile
"""

import os
import re
import shutil
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command, Platform
from file_mod import FileUtil
from subtask_mod import Background, Daemon, Exec
from task_mod import Tasks


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_pattern(self) -> str:
        """
        Return filter patern.
        """
        return self._pattern

    def get_firefox(self) -> Command:
        """
        Return Firefox Command class object.
        """
        return self._firefox

    @staticmethod
    def _get_profiles_dir() -> Path:
        if Platform.get_system() == 'macos':
            return Path(
                'Library',
                'Application Support',
                'Firefox',
                'Profiles',
            )
        return Path('.mozilla', 'firefox')

    @staticmethod
    def _remove_lock(firefox_path: Path) -> None:
        # Remove old session data and lock file (allows multiple instances)
        for path in (
            list(firefox_path.glob('*/sessionstore.js')) +
            list(firefox_path.glob('*/.parentlock')) +
            list(firefox_path.glob('*/lock')) +
            list(firefox_path.glob('*/*.log'))
        ):
            try:
                path.unlink()
            except OSError:
                continue

    @staticmethod
    def _remove_junk_files(firefox_path: Path) -> None:
        ispattern = re.compile(
            '^(lastDownload|lastSuccess|lastCheck|expires|'
            r'softExpiration)=\d*'
        )
        for path in firefox_path.glob('*/adblockplus/patterns.ini'):
            path_new = Path(f'{path}.part')
            try:
                with path.open(errors='replace') as ifile:
                    with path_new.open('w') as ofile:
                        for line in ifile:
                            if not ispattern.search(line):
                                print(line, end='', file=ofile)
            except OSError:
                try:
                    path_new.unlink()
                except OSError:
                    continue
            else:
                try:
                    path_new.replace(path)
                except OSError:
                    continue

    @staticmethod
    def _fix_xulstore(firefox_path: Path) -> None:
        for directory in firefox_path.glob('*'):
            path = Path(directory, 'xulstore.json')
            path_new = Path(f'{path}.part')
            try:
                with path.open(errors='replace') as ifile:
                    with path_new.open('w') as ofile:
                        for line in ifile:
                            print(
                                line.replace('"fullscreen"', '"maximized"'),
                                end='',
                                file=ofile,
                            )
            except OSError:
                try:
                    path_new.unlink()
                except OSError:
                    pass
            else:
                try:
                    path_new.replace(path)
                except OSError:
                    pass

    def _fix_installation(self) -> None:
        file = self._firefox.get_file()
        if Path(f'{file}-bin').is_file():
            fmod = Command('fmod', errors='ignore')
            if fmod.is_found():
                # Fix permissions if owner and updated
                fmod.set_args(['wa', Path(self._firefox.get_file()).parent])
                Daemon(fmod.get_cmdline()).run()

    def _config(self) -> None:
        path = Path(Path.home(), self._get_profiles_dir())
        if path.is_dir():
            path.chmod(0o700)
            self._remove_lock(path)
            self._remove_junk_files(path)
            self._fix_xulstore(path)

        self._fix_installation()

    @staticmethod
    def _remove(path: Path) -> None:
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        except OSError:
            pass

    def _reset(self) -> None:
        firefox_path = Path(Path.home(), self._get_profiles_dir())
        if firefox_path.is_dir():
            keep_list = (
                'addonStartup.json.lz4',
                'content-prefs.sqlite',
                'extensions',
                'extensions.json',
                'extension-preferences.json',
                'handlers.json',
                'permissions.sqlite',
                'prefs.js',
                'search.json.mozlz4',
                'storage',
                'storage.sqlite',
                'user.js',
                'xulstore.json'
            )
            for directory in firefox_path.glob('*'):
                if Path(directory, 'prefs.js').is_file():
                    for path in list(directory.glob('*')):
                        if path.name not in keep_list:
                            print(f'Removing "{path}"...')
                            self._remove(path)
                    for path in directory.glob(
                        'adblockplus/patterns-backup*ini'
                    ):
                        path.unlink()

    @classmethod
    def _prefs(cls) -> None:
        # Check Invalidprefs.js for errors
        settings = [f'user_pref({x});' for x in (
            '"accessibility.typeaheadfind.enablesound", false',
            '"beacon.enabled", false',
            '"browser.aboutHomeSnippets.updateUrl", ""',
            '"browser.blink_allowed", false',
            '"browser.bookmarks.max_backups", 1',
            '"browser.safebrowsing.enabled", false',
            '"browser.safebrowsing.malware.enabled", false',
            '"browser.cache.disk.enable", false',
            '"browser.cache.memory.capacity", 16384',
            '"browser.display.show_image_placeholders", false',
            '"browser.download.animateNotifications", false',
            '"browser.download.improvements_to_download_panel", false',
            '"browser.link.open_external", 3',
            '"browser.link.open_newwindow.restriction", 0',
            '"browser.ml.enabled", false',
            '"browser.ml.chat.enabled", false',
            '"browser.newtabpage.enabled", false',
            '"browser.newtabpage.activity-stream.feeds.telemetry", false',
            '"browser.newtabpage.activity-stream.telemetry", false',
            '"browser.newtabpage.activity-stream.telemetry.ping.endpoint", ""',
            '"browser.ping-centre.production.endpoint", ""',
            '"browser.ping-centre.staging.endpoint", ""',
            '"browser.ping-centre.telemetry", false',
            '"browser.search.geoip.url", ""',
            '"browser.sessionstore.interval", 86400000',
            '"browser.tabs.allowTabDetach", false',
            '"browser.tabs.animate", false',
            '"browser.tabs.groups.enabled", false',
            '"browser.tabs.insertRelatedAfterCurrent", false',
            '"browser.tabs.tabmanager.enabled", false',
            '"browser.urlbar.autoFill", false',
            '"browser.urlbar.decodeURLsOnCopy", true',
            '"browser.urlbar.speculativeConnect.enabled", false',
            '"browser.urlbar.trimURLs", false',
            '"browser.sessionhistory.max_total_viewers", 0',
            '"browser.sessionhistory.max_viewers", 0',
            '"browser.sessionhistory.sessionhistory.max_entries", 5',
            '"browser.sessionstore.resume_from_crash", false',
            '"browser.sessionstore.max_resumed_crashes", 0',
            '"browser.sessionstore.max_tabs_undo", 0',
            '"browser.shell.checkDefaultBrowser", false',
            '"browser.tabs.tabmanager.enabled", false',
            '"browser.zoom.siteSpecific", false',
            '"content.interrupt.parsing", true',
            '"content.notify.backoffcount", 5',
            '"content.notify.interval", 500000',
            '"dom.battery.enabled", false',
            '"dom.event.contextmenu.enabled", false',
            '"dom.max_script_run_time", 20',
            '"dom.push.enabled", false',
            '"dom.push.serverURL", ""',
            '"dom.serviceWorkers.enabled", false',
            '"extensions.blocklist.enabled", false',
            '"extensions.unifiedExtensions.enabled", false',
            '"geo.wifi.uri", ""',
            '"full-screen-api.approval-required", false',
            '"geo.enabled", false',
            '"layout.frames.force_resizability", true',
            '"layout.spellcheckDefault", 2',
            '"loop.throttled", false',
            '"media.autoplay.allow-extension-background-pages", false',
            '"media.autoplay.block-event.enabled", true',
            '"media.autoplay.blocking_policy", 2',
            '"media.autoplay.default", 5',
            '"media.fragmented-mp4.exposed", true',
            '"media.fragmented-mp4.ffmpeg.enabled", true',
            '"media.fragmented-mp4.gmp.enabled", false',
            '"media.gstreamer.enabled", false',
            '"media.navigator.enabled", false',
            '"mousewheel.min_line_scroll_amount", 2',
            '"network.captive-portal-service.enabled", false',
            '"network.dns.disablePrefetch", true',
            '"network.http.pipelining.maxrequests", 8',
            '"network.http.pipelining", true',
            '"network.http.proxy.pipelining", true',
            '"network.http.speculative-parallel-limit", 0',
            '"network.prefetch-next", false',
            '"network.proxy.socks_remote_dns", true',
            '"nglayout.initialpaint.delay", 0',
            '"pdfjs.enableScripting", false',
            '"print.print_edge_bottom", 20',
            '"print.print_edge_left", 20',
            '"print.print_edge_right", 20',
            '"print.print_edge_top", 20',
            '"privacy.popups.showBrowserMessage", false',
            '"reader.parse-on-load.enabled", false',
            '"security.dialog_enable_delay", 0',
            '"toolkit.storage.synchronous", 0',
            '"toolkit.telemetry.archive.enabled", false',
            '"toolkit.telemetry.bhrPing.enabled", false',
            '"toolkit.telemetry.firstShutdownPing.enabled", false',
            '"toolkit.telemetry.hybridContent.enabled", false',
            '"toolkit.telemetry.newProfilePing.enabled", false',
            '"toolkit.telemetry.shutdownPingSender.enabled", false',
            '"toolkit.telemetry.unified", false',
            '"toolkit.telemetry.updatePing.enabled", false',
            '"ui.submenuDelay", 0',
        )]

        firefox_path = Path(Path.home(), cls._get_profiles_dir())
        if firefox_path.is_dir():
            for path in firefox_path.glob('*/prefs.js'):
                try:
                    with path.open(errors='replace') as ifile:
                        lines = [x.rstrip() for x in ifile.readlines()]
                    if not set(settings).issubset(set(lines)):
                        with path.open('a') as ofile:
                            for setting in settings:
                                if setting not in lines:
                                    print(setting, file=ofile)
                except OSError:
                    pass

    @classmethod
    def _redirect_tmpdir(cls, path: Path) -> None:
        tmpdir = FileUtil.tmpdir(path.name)
        if not path.is_symlink():
            cls._remove(path)
            path.symlink_to(tmpdir)

    @classmethod
    def fix_storage(cls) -> None:
        """
        Redirect large extensipn storgae to TMPDIR
        """
        firefox_path = Path(Path.home(), cls._get_profiles_dir())
        if firefox_path.is_dir():
            for path in firefox_path.glob('*/storage/default/moz-extension*'):
                if path.is_symlink():
                    cls._redirect_tmpdir(path)  # Re-create symlink
            for path in firefox_path.glob(
                '*/storage/default/moz-extension*/*/*.sqlite'
            ):
                matches = FileUtil.strings(path, 'video|downloaded', full=True)
                if 'video' in matches and 'downloaded' in matches:
                    cls._redirect_tmpdir(Path(str(path).split('^', 1)[0]))

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        pathextra = (
            ['/Applications/Firefox.app/Contents/MacOS']
            if Platform.get_system() == 'macos' else []
        )
        self._firefox = Command(
            Path(args[0]).stem,
            pathextra=pathextra,
            errors='stop',
        )

        if len(args) > 1:
            if args[1] == '-reset':
                self._reset()
                raise SystemExit(0)
            if args[1] in ('-v', '-V', '-version', '--version'):
                self._firefox.set_args(['--version'])
                Exec(self._firefox.get_cmdline()).run()

        # Avoids 'exo-helper-1 firefox http://' prob of clicking text in XFCE
        if len(args) > 1:
            ppid = os.getppid()
            if (
                ppid != 1 and
                'exo-helper' in Tasks.factory().get_process(ppid)['COMMAND']
            ):
                raise SystemExit

        self._firefox.extend_args(args[1:])
        self._pattern = (
            '^$|Failed to load module|: G[dt]k-WARNING |: G[dt]k-CRITICAL |:'
            ' GLib-GObject-|: GnomeUI-WARNING|^OpenGL Warning: |'
            ' Pango-WARNING |^WARNING: Application calling GLX |'
            ': libgnomevfs-WARNING |: wrong ELF class|'
            '(child|parent) won, so we|processing deferred in-call|'
            'is not defined|^failed to create drawable|'
            'None of the authentication protocols|'
            'NOTE: child process received|: Not a directory|[/ ]thumbnails |'
            ': Connection reset by peer|'
        )

        self._config()
        self._prefs()


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        cmdline = options.get_firefox().get_cmdline()
        Background(cmdline).run(pattern=options.get_pattern())
        options.fix_storage()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
