#!/usr/bin/env python3
"""
Menu for launching software
"""

import argparse
import glob
import os
import signal
import sys

import jinja2
import yaml

import command_mod
import file_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    def get_names(self):
        """
        Return menu names.
        """
        return self._args.names

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Menu for launching software')

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show TCL file.'
        )
        parser.add_argument(
            'names',
            nargs='*',
            metavar='name',
            default=['main'],
            help='Menu name.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Menu:
    """
    Menu class
    """

    def __init__(self, options):
        self._view_flag = options.get_view_flag()
        self._names = options.get_names()

        template = sys.argv[0].rsplit('.py', 1)[0] + '.tcl.jinja2'
        with open(template) as ifile:
            self._template = jinja2.Template(ifile.read())
        config = sys.argv[0].rsplit('.py', 1)[0] + '.yaml'
        with open(config) as ifile:
            self._config = yaml.safe_load(ifile.read())

    @staticmethod
    def check_software(check):
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

    def generate(self, name):
        """
        Render template and return lines.
        """
        items = self._config.get('menu_' + name)
        if not items:
            raise SystemExit("{0:s}: Cannot find in menu.yaml: {1:s}".format(
                sys.argv[0],
                name,
            ))

        config = {'buttons': []}
        config['title'] = name
        for item in items:
            if self.check_software(item.get('check')):
                config['buttons'].append(item['button'])

        lines = self._template.render(config).split('\n')

        return lines

    def open(self):
        """
        Open menus
        """
        wish = command_mod.Command('wish', errors='stop')
        tmpdir = file_mod.FileUtil.tmpdir(os.path.join('.cache', 'menu'))

        for name in self._names:
            file = os.path.join(tmpdir, name + '.tcl')
            try:
                with open(file, 'w', newline='\n') as ofile:
                    for line in self.generate(name):
                        if self._view_flag:
                            print(line)
                        print(line, file=ofile)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + file + '" file.',
                ) from exception

            subtask_mod.Background(wish.get_cmdline() + [file]).run()


class Main:
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

        Menu(options).open()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
