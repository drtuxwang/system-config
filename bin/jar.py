#!/usr/bin/env python3
"""
JAVA jar tool launcher
"""

import glob
import os
import signal
import sys
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._files

    def get_jar(self) -> command_mod.Command:
        """
        Return jar Command class object.
        """
        return self._jar

    def get_jar_file(self) -> str:
        """
        Return jar file location.
        """
        return self._jar_file

    def get_manifest(self) -> str:
        """
        Return manifest file location.
        """
        return self._manifest

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._jar = command_mod.Command(
            os.path.join('bin', 'jar'),
            errors='stop'
        )

        if len(args) == 1:
            subtask_mod.Exec(self._jar.get_cmdline()).run()
        elif args[1][-4:] != '.jar':
            self._jar.set_args(args[1:])
            subtask_mod.Exec(self._jar.get_cmdline()).run()

        self._jar_file = args[1]
        self._manifest = args[1][:-4] + '.manifest'
        self._files = args[2:]
        self._jar.set_args(['cfvm', args[1], self._manifest])


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
    def _compile(source: str) -> None:
        target = source[:-5]+'.class'
        if not os.path.isfile(source):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "{source}" Java source file.',
            )
        if os.path.isfile(target):
            if os.path.getmtime(source) > os.path.getmtime(target):
                try:
                    os.remove(target)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot remove '
                        f'"{target}" Java class file.',
                    ) from exception
        if not os.path.isfile(target):
            javac = command_mod.Command('javac', args=[source], errors='stop')
            print(f'Building "{target}" Java class file.')
            task = subtask_mod.Batch(javac.get_cmdline())
            task.run(error2output=True)
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )
            for line in task.get_output():
                print(f"  {line}")
            if not os.path.isfile(target):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{target}" Java class file.'
                )

    def _create_manifest(self) -> None:
        if not os.path.isfile(self._manifest):
            if 'Main.class' in self._jar.get_args():
                main = 'Main'
            else:
                main = self._jar_file[:-4]
            print(
                f'Building "{self._manifest}" Java manifest file with '
                f'"{main}" main class.',
            )
            try:
                with open(
                    self._manifest,
                    'w',
                    encoding='utf-8',
                    newline='\n',
                ) as ofile:
                    print("Main-Class:", main, file=ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create '
                    f'"{self._manifest}" Java manifest file.',
                ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._jar = options.get_jar()
        self._jar_file = options.get_jar_file()
        self._manifest = options.get_manifest()

        for file in options.get_files():
            if file.endswith('.java'):
                self._compile(file)
                self._jar.append_arg(file[:-5]+'.class')
            else:
                self._jar.append_arg(file)
        self._create_manifest()
        print(f'Building "{self._jar_file}" Java archive file.')
        subtask_mod.Exec(self._jar.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
