#!/usr/bin/env python3
"""
Wrapper for "geeqie" command
"""

import glob
import json
import os
import re
import random
import signal
import shutil
import sys
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
        home = os.environ.get('HOME', '')
        configdir = os.path.join(home, '.config', 'geeqie')
        if not os.path.isdir(configdir):
            try:
                os.makedirs(configdir)
            except OSError:
                return
        file = os.path.join(configdir, 'history')
        if not os.path.isdir(file):
            try:
                if os.path.isfile(file):
                    os.remove(file)
                os.mkdir(file)
            except OSError:
                pass
        file = os.path.join(configdir, 'geeqierc.xml')
        try:
            with open(file, 'rb') as ifile:
                data = ifile.read()
            if b'hidden = "true"' in data:
                data = data.replace(b'hidden = "true"', b'hidden = "false"')
                with open(file+'-new', 'wb') as ofile:
                    ofile.write(data)
                shutil.move(file+'-new', file)
        except OSError:
            pass

        for file in (
                os.path.join(home, '.cache', 'geeqie', 'thumbnails'),
                os.path.join(home, '.local', 'share', 'geeqie'),
        ):
            if not os.path.isfile(file):
                try:
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                    with open(file, 'wb'):
                        pass
                except OSError:
                    pass

    @staticmethod
    def select(directories: List[str]) -> str:
        """
        Select directory randomly
        """
        tmpdir = file_mod.FileUtil.tmpdir('.cache')
        configfile = os.path.join(tmpdir, 'gqview.json')
        config = Configuration(configfile)
        config.set_choices(directories)
        directory = config.get_choice(directories)
        config.write(configfile + '.part')
        try:
            shutil.move(configfile + '.part', configfile)
        except OSError:
            os.remove(configfile + '.part')
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
                if not os.path.isdir(arg):
                    self._gqview.set_args(args[1:])
                    return

            directories = [
                x
                for x in args[1:]
                if glob.glob(os.path.join(x, '*'))
            ]
            directory = self.select(directories)
            print("GQView selection:", directory)
            self._gqview.set_args([directory])


class Configuration:
    """
    Configuration class
    """

    def __init__(self, file: str = '') -> None:
        self._data: dict = {'gqview': {}}
        if file:
            try:
                with open(file, encoding='utf-8', errors='replace') as ifile:
                    self._data = json.load(ifile)
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

    def write(self, file: str) -> None:
        """
        Write file
        """
        try:
            with open(file, 'w', encoding='utf-8', newline='\n') as ofile:
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
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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
