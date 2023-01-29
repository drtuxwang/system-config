#!/usr/bin/env python3
"""
Wrapper for "wget" command
"""

import os
import shutil
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import network_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_output(self) -> str:
        """
        Return output file.
        """
        return self._output

    def get_wget(self) -> command_mod.Command:
        """
        Return wget Command class object.
        """
        return self._wget

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._wget = command_mod.Command('wget', errors='stop')
        if '--hsts-file=/dev/null' not in args:
            self._wget.append_arg('--hsts-file=/dev/null')
        if '--no-check-certificate' not in args:
            self._wget.append_arg('--no-check-certificate')
        if '--timestamping' not in args:
            self._wget.append_arg('--timestamping')

        # Replace '-O' with '--output-document'
        args = ['--output-document' if x == '-O' else x for x in args]

        # Add '--output-document' for Firefox
        if '--output-document' not in args:
            for arg in args:
                if arg.startswith('--user-agent=') and 'Firefox/' in arg:
                    self._wget.extend_args(
                        ['--output-document', Path(args[-1]).name])
                    break

        self._output = ''
        while len(args) > 1:
            if (len(args) > 2 and args[1] in ('--output-document', '-O') and
                    not args[2].endswith(('-', '.part'))):
                self._output = args[2]
                if Path(args[2]).is_file():
                    raise SystemExit(f"Output file already exists: {args[2]}")
                self._wget.extend_args([args[1], self._output + '.part'])
                args = args[2:]
                continue
            self._wget.append_arg(args[1])
            args = args[1:]


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
        output = options.get_output()
        wget = options.get_wget()

        cmdline = wget.get_cmdline()
        netnice = network_mod.NetNice()
        if netnice.is_found():
            cmdline = netnice.get_cmdline() + cmdline

        if output:
            task = subtask_mod.Task(cmdline)
            task.run()
            if (
                    task.get_exitcode() or
                    not Path(f'{output}.part').is_file() or
                    Path(f'{output}.part').stat().st_size == 0
            ):
                raise SystemExit(task.get_exitcode())
            try:
                shutil.move(output + '.part', output)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{output}" output file.',
                ) from exception
        else:
            subtask_mod.Exec(cmdline).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
