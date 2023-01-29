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

import command_mod
import file_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_gqview(self) -> command_mod.Command:
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
            with path.open('rb') as ifile:
                data = ifile.read()
            if b'hidden = "true"' in data:
                data = data.replace(b'hidden = "true"', b'hidden = "false"')
                path_new = Path(f'{path}-new')
                with path_new.open('wb') as ofile:
                    ofile.write(data)
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
    def select(directories: List[str]) -> str:
        """
        Select directory randomly
        """
        tmpdir = file_mod.FileUtil.tmpdir('.cache')
        path = Path(tmpdir, 'gqview.json')
        config = Configuration(path)
        config.set_choices(directories)
        directory = config.get_choice(directories)

        path_new = Path(f'{path}.part')
        config.write(path_new)
        try:
            path_new.replace(path)
        except OSError:
            path_new.unlink()
        return directory

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._gqview = command_mod.Command('geeqie', errors='ignore')
        if self._gqview.is_found():
            self._config_geeqie()
        else:
            self._gqview = command_mod.Command('gqview', errors='stop')
        if len(args) == 1:
            self._gqview.set_args([os.curdir])
        else:
            for arg in args[1:]:
                if not Path(arg).is_dir():
                    self._gqview.set_args(args[1:])
                    return

            directories = [x for x in args[1:] if list(Path(x).glob('*'))]
            directory = self.select(directories)
            print("GQView selection:", directory)
            self._gqview.set_args([directory])


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

    def get_choice(self, directories: List[str]) -> str:
        """
        Return next choice
        """
        key = str(directories)
        choices = self._data['gqview'][key]
        choice = choices[0]
        self._data['gqview'][key] = choices[1:] + [choice]
        return choice

    def set_choices(self, directories: List[str]) -> None:
        """
        If new choices shuffle directory
        """
        key = str(directories)
        if key not in self._data['gqview']:
            ismatch = re.compile(r'_\d+$')
            weights = []
            for directory in directories:
                if ismatch.search(directory):
                    weights.append(int(directory.rsplit('_')[-1]))
                else:
                    weights.append(1)
            choices: List[str] = []
            while len(choices) < len(directories):
                choices.extend(random.choices(directories, weights, k=128))
                choices = list(dict.fromkeys(choices))
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
        subtask_mod.Daemon(options.get_gqview().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
