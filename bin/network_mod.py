#!/usr/bin/env python3
"""
Python network handling utility module

Copyright GPL v2: 2015-2021 By Dr Colin Kong
"""

import json
import os
from typing import Optional

import command_mod

RELEASE = '3.0.0'
VERSION = 20210722


class NetNice(command_mod.Command):
    """
    NetNice network traffic shaping command class
    """

    def __init__(
        self,
        drate: Optional[int] = None,
        errors: str = 'ignore',
    ) -> None:
        super().__init__('trickle', errors=errors)

        self._drate = 8000
        home = os.environ.get('HOME', '')
        file = os.path.join(home, '.config', 'netnice.json')
        if not self.read(file):
            self.write(file)

        if drate:
            self._drate = drate

        self.set_rate(self._drate)

    def set_rate(self, drate: int) -> None:
        """
        Set rate

        drate = Download rate (KB)
        """
        self._drate = drate
        self.set_args(['-d', str(self._drate), '-s'])

    def read(self, file: str) -> bool:
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

    def write(self, file: str) -> None:
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


if __name__ == '__main__':
    help(__name__)
