#!/usr/bin/env python3
"""
Wrapper for "pidgin" command
"""

import os
import re
import signal
import sys
from pathlib import Path

from command_mod import Command
from subtask_mod import Background


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
    def _config() -> None:
        path = Path(Path.home(), '.purple', 'prefs.xml')
        path_new = Path(f'{path}.part')
        try:
            with path.open(errors='replace') as ifile:
                try:
                    with path_new.open('w') as ofile:
                        # Disable logging of chats
                        islog = re.compile('log_.*type="bool"')
                        for line in ifile:
                            if islog.search(line):
                                line = line.rstrip().replace('1', '0')
                            print(line, file=ofile)
                except OSError:
                    return
        except OSError:
            return
        try:
            path_new.replace(path)
        except OSError:
            pass

    def run(self) -> int:
        """
        Start program
        """
        pidgin = Command('pidgin', args=sys.argv[1:], errors='stop')
        self._config()

        Background(pidgin.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
