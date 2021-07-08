#!/usr/bin/env python3
"""
Wrapper for "helm" command
"""

import glob
import os
import shutil
import signal
import sys

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
    def _cache() -> None:
        helm2_directory = os.path.join(os.environ['HOME'], '.helm')
        if os.path.isdir(helm2_directory):
            if not os.path.isdir(os.path.join(helm2_directory, 'repository')):
                try:
                    os.makedirs(os.path.join(helm2_directory, 'repository'))
                except OSError:
                    return

            for cache in ('cache', 'repository/cache'):
                link = os.path.join(helm2_directory, cache)

                directory = file_mod.FileUtil.tmpdir(os.path.join(
                    '.cache',
                    'helm',
                    cache.split(os.sep, 1)[0],
                ))
                if not os.path.islink(link):
                    try:
                        if os.path.exists(link):
                            shutil.rmtree(link)
                        os.symlink(directory, link)
                    except OSError:
                        pass

        directory = file_mod.FileUtil.tmpdir(
            os.path.join('.cache', 'helm', 'repository')
        )
        if not glob.glob(os.path.join(directory, '*-index.yaml')):
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
