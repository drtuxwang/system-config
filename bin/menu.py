#!/usr/bin/env python3
"""
Menu for launching software
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import jinja2  # type: ignore

import command_mod
import config_mod
import file_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def get_menus(self) -> List[str]:
        """
        Return menu names.
        """
        return self._args.menus

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Menu for launching software',
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show TCL file.'
        )
        parser.add_argument(
            'menus',
            nargs='*',
            metavar='menu',
            default=['main'],
            help='Menu name.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Menu:
    """
    Menu class
    """

    def __init__(self, options: Options) -> None:
        self._view_flag = options.get_view_flag()
        self._menus = options.get_menus()

        template = sys.argv[0].rsplit('.py', 1)[0] + '.tcl.jinja2'
        with open(template) as ifile:
            self._template = jinja2.Template(ifile.read())

        config_file = sys.argv[0].rsplit('.py', 1)[0] + '.yaml'
        status_file = os.path.join(
            os.environ['HOME'],
            '.config',
            os.path.basename(sys.argv[0]).rsplit('.py', 1)[0] + '.json',
        )
        if os.path.isfile(status_file):
            file = status_file
        else:
            file = config_file

        data = config_mod.Data()
        data.read(file)
        self._config = next(data.get())

        if self._menus == ['main']:
            self.update(config_file, status_file)

    @staticmethod
    def check_software(check: str) -> bool:
        """
        Return True if software found.
        """
        if not check:
            return True

        for directory in os.environ.get('PATH', '').split(os.pathsep):
            if glob.glob(
                    os.path.join(os.path.dirname(directory), '*', '*', check)
            ):
                return True
            if os.sep in check:
                if os.path.exists(os.path.join(directory, check)):
                    return True
            file = os.path.join(directory, os.path.basename(check))
            if os.path.exists(file) and not os.path.exists(file + '.py'):
                return True
        return False

    def generate(self, menu: str) -> List[str]:
        """
        Render template and return lines.
        """
        items = self._config.get('menu_' + menu)
        if not items:
            raise SystemExit("{0:s}: Cannot find in menu.yaml: {1:s}".format(
                sys.argv[0],
                menu,
            ))

        config: dict = {'buttons': []}
        config['title'] = menu
        for item in items:
            if self.check_software(item.get('check')):
                config['buttons'].append(item['button'])

        lines = self._template.render(config).split('\n')

        return lines

    def open(self) -> None:
        """
        Open menus
        """
        wish = command_mod.Command('wish', errors='stop')
        tmpdir = file_mod.FileUtil.tmpdir(os.path.join('.cache', 'menu'))

        for menu in self._menus:
            file = os.path.join(tmpdir, menu + '.tcl')
            try:
                with open(file, 'w', newline='\n') as ofile:
                    for line in self.generate(menu):
                        if self._view_flag:
                            print(line)
                        print(line, file=ofile)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + file + '" file.',
                ) from exception

            subtask_mod.Background(wish.get_cmdline() + [file]).run()

    @classmethod
    def update(cls, config_file: str, status_file: str) -> None:
        """
        Update status file
        """
        data = config_mod.Data()
        data.read(config_file)
        config = next(data.get())

        for menu in [x for x in config if x.startswith('menu')]:
            found = []
            for item in config[menu]:
                check = item.get('check')
                if check:
                    if not cls.check_software(check):
                        continue
                    del item['check']
                found.append(item)
            config[menu] = found

        if os.path.isfile(status_file):
            data.read(status_file)
            status = next(data.get())
            if config == status:
                return
            print("Updating status file:", status_file)
        else:
            print("Writing status file:", status_file)

        data.set([config])
        data.write(status_file, compact=True)


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

        Menu(options).open()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
