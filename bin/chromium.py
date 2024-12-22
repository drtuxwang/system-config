#!/usr/bin/env python3
"""
Wrapper for "chromium" command

Use '-copy' to copy profile to '/tmp'
Use '-reset' to clean junk from profile
Use '-restart' to restart chromium
"""

import json
import os
import re
import shutil
import signal
import sys
from pathlib import Path
from typing import Any, List

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
        Return filter pattern.
        """
        return self._pattern

    def get_browser(self) -> Command:
        """
        Return browser Command class object.
        """
        return self._browser

    @staticmethod
    def _get_profiles_dir() -> Path:
        if Platform.get_system() == 'macos':
            return Path('Library', 'Application Support', 'Chromium')
        return Path('.config', 'google-chrome')

    @staticmethod
    def _clean_preferences(config_path: Path) -> None:
        path = Path(config_path, 'Preferences')
        path_new = Path(f'{path}.part')
        try:
            data = json.loads(path.read_text(errors='replace'))
            data['profile']['exit_type'] = 'Normal'
            data['partition']['per_host_zoom_levels'] = {}
            with path_new.open('w') as ofile:
                print(json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                ), file=ofile)
        except (KeyError, OSError, ValueError):
            try:
                path_new.unlink()
            except OSError:
                pass
        else:
            try:
                path_new.replace(path)
            except OSError:
                pass

    @staticmethod
    def _clean_junk_files(config_path: Path) -> None:
        for fileglob in (
            'Archive*',
            'Cookies*',
            'Current*',
            'History*',
            'Last*',
            'Visited*',
            'Last*',
        ):
            for path in config_path.glob(fileglob):
                try:
                    path.unlink()
                except OSError:
                    pass
        ispattern = re.compile(
            r'^(lastDownload|lastSuccess|lastCheck|expires|softExpiration)=\d*'
        )
        for path in config_path.glob('File System/*/p/00/*'):
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

    def _config(self) -> None:
        path = Path(Path.home(), self._get_profiles_dir(), 'Default')

        if path.is_dir():
            self._clean_preferences(path)
            self._clean_junk_files(path)

    def _copy(self) -> None:
        task = Tasks.factory()
        tmpdir = FileUtil.tmpdir('.cache')
        for path in Path(tmpdir).glob('chromium.*'):
            try:
                if not task.pgid2pids(int(path.suffix)):
                    print(
                        f'Removing copy of Chrome profile in "{path}"...',
                    )
                    try:
                        shutil.rmtree(path)
                    except OSError:
                        pass
            except ValueError:
                pass

        home = Path.home()
        config_path = Path(home, self._get_profiles_dir())
        mypid = os.getpid()
        os.setpgid(mypid, mypid)  # New PGID

        newhome = FileUtil.tmpdir(Path(tmpdir, f'chromium.{mypid}'))
        print(f'Creating copy of Chromium profile in "{newhome}"...')
        if not Path(newhome).is_dir():
            try:
                shutil.copytree(
                    config_path,
                    Path(newhome, self._get_profiles_dir())
                )
            except (OSError, shutil.Error):  # Ignore 'lock' file error
                pass
        try:
            Path(newhome, 'Desktop').symlink_to(Path(home, 'Desktop'))
        except OSError:
            pass
        os.environ['HOME'] = newhome

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
        config_path = Path(Path.home(), self._get_profiles_dir())
        if config_path.is_dir():
            keep_list = (
                'Extensions',
                'File System',
                'Local Extension Settings',
                'Local Storage',
                'Preferences',
                'Secure Preferences'
            )
            for directory in config_path.glob('*'):
                if Path(directory, 'Preferences').is_file():
                    for path in directory.glob('*'):
                        if path.name not in keep_list:
                            print(f'Removing "{path}"...')
                            self._remove(path)
                elif (
                    directory.name not in
                    {'Extensions', 'First Run', 'Local State'}
                ):
                    print(f'Removing "{directory}"...')
                    self._remove(directory)
                for path in directory.glob('Local Storage/https*'):
                    self._remove(path)
                for path in directory.glob('.???*'):
                    print(f'Removing "{path}"...')
                    self._remove(path)

    def _restart(self) -> None:
        path = Path(Path.home(), self._get_profiles_dir(), 'SingletonLock')
        try:
            pid = int(str(
                # pylint: disable=no-member
                path.readlink()  # type: ignore
                # pylint: enable=no-member
            ).split('-')[1])
            Tasks.factory().killpids([pid])
        except (IndexError, OSError):
            pass

    @staticmethod
    def _set_libraries(command: Command) -> None:
        path = Path(command.get_file()).with_name('lib')
        if path.is_dir() and os.name == 'posix':
            if os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        f"{path}{os.pathsep}{os.environ['LD_LIBRARY_PATH']}"
                    )
                else:
                    os.environ['LD_LIBRARY_PATH'] = str(path)

    @staticmethod
    def _locate() -> Command:
        commands = ['chromium-browser', 'chromium']
        for command in commands:
            browser = Command(command, errors='ignore')
            if browser.is_found():
                return browser
        return Command('chromium', errors='stop')

    def parse(self, args: List[str]) -> None:

        """
        Parse arguments
        """
        self._browser = self._locate()

        if len(args) > 1:
            if args[1] == '-version':
                self._browser.set_args(['-version'])
                Exec(self._browser.get_cmdline()).run()
            elif args[1] == '-copy':
                self._copy()
            elif args[1] == '-reset':
                self._reset()
                raise SystemExit(0)

            if args[1] == '-restart':
                self._restart()
                args = args[1:]
            self._browser.set_args(args[1:])

        # Avoids 'exo-helper-1 chrome http://' problem of clicking text in XFCE
        if len(args) > 1:
            ppid = os.getppid()
            if (
                ppid != 1 and
                'exo-helper' in Tasks.factory().get_process(ppid)['COMMAND']
            ):
                raise SystemExit

        if '--disable-background-mode' not in self._browser.get_args():
            self._browser.extend_args([
                '--disable-background-mode',
                '--disable-geolocation',
                '--disable-infobars',
                '--disk-cache-dir=/dev/null',
                '--disk-cache-size=1',
                '--password-store=basic',
                '--process-per-site',
                '--site-per-process',
            ])

        # No sandbox workaround
        if not Path('/opt/google/chrome/chrome-sandbox').is_file():
            self._browser.append_arg('--no-sandbox')

        self._pattern = (
            '^$|^NPP_GetValue|NSS_VersionCheck| Gtk:|: GLib-GObject-CRITICAL|'
            ' GLib-GObject:|: no version information available|:ERROR:.*[.]cc|'
            'Running without renderer sandbox|:Gdk-WARNING |: DEBUG: |^argv|'
            ': cannot adjust line|^Created new window|Unable to revert mtime:|'
            'internal-pdf-viewer:|LIBDBUSMENU-GLIB-WARNING|'
            '^Opening in existing browser'
        )
        self._config()
        self._set_libraries(self._browser)


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
        if sys.version_info < (3, 9):
            def _readlink(file: Any) -> Path:
                return Path(os.readlink(file))
            Path.readlink = _readlink  # type: ignore

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        cmdline = options.get_browser().get_cmdline()
        Background(cmdline).run(pattern=options.get_pattern())

        # Kill filtering process after start up to avoid hang
        tkill = Command(
            'tkill',
            args=['-delay', '60', '-f', f'python3.* {cmdline[0]} '],
            errors='ignore'
        )
        if tkill.is_found():
            Daemon(tkill.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
