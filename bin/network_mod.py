#!/usr/bin/env python3
"""
Python network handling utility module

Copyright GPL v2: 2015-2021 By Dr Colin Kong
"""

import json
import os

import command_mod

RELEASE = '3.1.0'
VERSION = 20210724


class NetNice(command_mod.Command):
    """
    NetNice network traffic shaping command class
    """

    def __init__(self, drate: int = 8000, errors: str = 'ignore') -> None:
        """
        drate = Download rate (default 8000kbps)
        errors = Optional error handling ('stop' or 'ignore')
        """
        self._drate = drate

        home = os.environ.get('HOME', '')
        file = os.path.join(home, '.config', 'netnice.json')
        if not self._read(file):
            self._write(file)

        # Try trickle bandwidth limits
        super().__init__('trickle', errors=errors)
        if self.is_found():
            self.set_args(['-d', str(self._drate), '-s'])

    def _read(self, file: str) -> bool:
        """
        Read configuration file
        """
        if os.path.isfile(file):
            try:
                with open(file) as ifile:
                    data = json.load(ifile)
                    self._drate = data['trickle']['download']
            except (KeyError, OSError, ValueError):
                pass
            else:
                return True

        return False

    def _write(self, file: str) -> None:
        """
        Write configuration file
        """
        data = {
            'trickle': {
                'download': self._drate
            }
        }
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=4,
                    sort_keys=True,
                ), file=ofile)
        except OSError:
            pass


class Sandbox(command_mod.Command):
    """
    Sandbox network command class
    """

    def __init__(self, errors: str = 'ignore') -> None:
        """
        errors = Optional error handling ('stop' or 'ignore')
        """
        # Try Bubblewrap network sandboxing
        super().__init__('bwrap', errors=errors)
        if self.is_found():
            self.set_args([
                '--bind',
                '/',
                '/',
                '--dev',
                '/dev',
                '--unshare-net',
                '--',
            ])


if __name__ == '__main__':
    help(__name__)
