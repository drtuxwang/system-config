#!/usr/bin/env python3
"""
Wrapper for "geeqie" command
"""

import json
import os
import re
import random
import signal
import shutil
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from file_mod import FileUtil
from subtask_mod import Daemon, Exec


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_gqview(self) -> Command:
        """
        Return gqview Command class object.
        """
        return self._gqview

    @staticmethod
    def _config_geeqie() -> None:
        home = Path.home()
        configdir = Path(home, '.config', 'geeqie')
        if not configdir.is_dir():
            try:
                os.makedirs(configdir)
            except OSError:
                return
        path = Path(configdir, 'history')
        if not path.is_dir():
            try:
                if Path(path).is_file():
                    path.unlink()
                path.mkdir()
            except OSError:
                pass
        path = Path(configdir, 'geeqierc.xml')
        try:
            data = path.read_text(errors='replace')
            data_new = data.replace('hidden = "true"', 'hidden = "false"')
            data_new = data_new.replace(
                'show_marks = "true"',
                'show_marks = "false"',
            )
            if data_new != data:
                path_new = Path(f'{path}-new')
                path_new.write_text(data_new)
                path_new.replace(path)
        except OSError:
            pass

        for path in (
            Path(home, '.cache', 'geeqie', 'thumbnails'),
            Path(home, '.local', 'share', 'geeqie'),
        ):
            if not path.is_file():
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    path.touch()
                except OSError:
                    pass

    @staticmethod
    def select(selections: List[str]) -> str:
        """
        Select file/directory randomly
        """
        tmpdir = FileUtil.tmpdir('.cache')
        path = Path(tmpdir, 'gqview.json')
        config = Configuration(path)
        config.set_choices(selections)
        selected = config.get_choice(selections)

        path_new = Path(f'{path}.part')
        config.write(path_new)
        try:
            path_new.replace(path)
        except OSError:
            path_new.unlink()
        return selected

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._gqview = Command('geeqie', errors='ignore')
        if self._gqview.is_found():
            self._config_geeqie()
        else:
            self._gqview = Command('gqview', errors='stop')

        paths = [Path(x) for x in args[1:]]
        for path in paths:
            if path.name in ('-v', '--version'):
                Exec(self._gqview.get_cmdline() + ['--version']).run()
            if not path.exists():
                self._gqview.set_args(args[1:])
                return
        selections = [
            str(x)
            for x in paths
            if x.is_file() or list(x.glob('*'))
            ]
        try:
            selected = self.select(selections)
            print("GQView selection:", selected)
            self._gqview.set_args([selected])
        except IndexError:
            self._gqview.set_args([os.curdir])


class Configuration:
    """
    Configuration class
    """

    def __init__(self, path: Path = None) -> None:
        self._data: dict = {'gqview': {}}
        if path:
            try:
                self._data = json.loads(path.read_text(errors='replace'))
            except (KeyError, OSError):
                pass

    def get_choice(self, selections: List[str]) -> str:
        """
        Return next choice
        """
        key = str(selections)
        choices = self._data['gqview'][key]
        choice = choices[0]
        self._data['gqview'][key] = choices[1:] + [choice]
        return choice

    def set_choices(self, selections: List[str]) -> None:
        """
        If new choices shuffle selections
        """
        key = str(selections)
        if key not in self._data['gqview']:
            ismatch = re.compile(r'_\d+$')
            weights = []
            for selection in selections:
                if ismatch.search(selection):
                    weights.append(int(selection.rsplit('_')[-1]))
                else:
                    weights.append(1)
            choices: List[str] = []
            while len(choices) < len(selections):
                choices.extend(random.choices(selections, weights, k=128))
                choices = list(dict.fromkeys(choices))  # Unique ordered list
            self._data['gqview'][key] = choices

    def write(self, path: Path) -> None:
        """
        Write file
        """
        try:
            with path.open('w') as ofile:
                print(json.dumps(
                    self._data,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                ), file=ofile)
        except OSError:
            pass


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
        # Geeqie hangs with filter/background
        Daemon(options.get_gqview().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
