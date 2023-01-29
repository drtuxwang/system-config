#!/usr/bin/env python3
"""
Wrapper for "helm" command
"""

import os
import shutil
import signal
import sys
from pathlib import Path

import command_mod
import file_mod
import subtask_mod


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
    def _cache() -> None:
        if command_mod.Platform.get_system() == 'macos':
            return
        helm2_directory = Path(Path.home(), '.helm')
        if helm2_directory.is_dir():
            if not Path(helm2_directory, 'repository').is_dir():
                try:
                    Path(helm2_directory, 'repository').mkdir(parents=True)
                except OSError:
                    return

            for cache in ('cache', 'repository/cache'):
                link = Path(helm2_directory, cache)

                directory = file_mod.FileUtil.tmpdir(Path(
                    '.cache',
                    'helm',
                    cache.split(os.sep, 1)[0],
                ))
                if not link.is_symlink():
                    try:
                        if link.exists():
                            shutil.rmtree(link)
                        link.symlink_to(directory)
                    except OSError:
                        pass

        directory = file_mod.FileUtil.tmpdir(
            Path('.cache', 'helm', 'repository')
        )
        if not list(Path(directory).glob('*-index.yaml')):
            helm = command_mod.Command('helm', errors='stop')
            task = subtask_mod.Batch(helm.get_cmdline() + ['repo', 'list'])
            task.run(pattern='http')
            if task.has_output():
                subtask_mod.Task(helm.get_cmdline() + ['repo', 'update']).run()

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        cls._cache()

        helm = command_mod.Command('helm', errors='stop')
        helm.set_args(sys.argv[1:])
        subtask_mod.Exec(helm.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
