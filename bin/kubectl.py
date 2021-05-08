#!/usr/bin/env python3
"""
Wrapper for "kubectl" command
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
        kube_directory = os.path.join(os.environ['HOME'], '.kube')
        if not os.path.isdir(kube_directory):
            try:
                os.mkdir(kube_directory)
            except OSError:
                return

        for cache in ('cache', 'http-cache'):
            link = os.path.join(kube_directory, cache)
            directory = file_mod.FileUtil.tmpdir(
                os.path.join('.cache', 'kube', cache)
            )
            if not os.path.islink(link):
                try:
                    if os.path.exists(link):
                        shutil.rmtree(link)
                    os.symlink(directory, link)
                except OSError:
                    pass

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        cls._cache()

        kubectl = command_mod.Command('kubectl', errors='stop')
        kubectl.set_args(sys.argv[1:])
        subtask_mod.Exec(kubectl.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
