#!/usr/bin/env python3
"""
Python network handling utility module

Copyright GPL v2: 2015-2019 By Dr Colin Kong
"""

import json
import os

import command_mod

RELEASE = '2.1.0'
VERSION = 20200721


class Shaper(command_mod.Command):
    """
    Shaper network traffic command class
    """

    def __init__(self, drate=None, errors='ignore'):
        super().__init__('trickle', errors=errors)

        self._drate = 512
        home = os.environ.get('HOME', '')
        file = os.path.join(home, '.config', 'trickle.json')
        if not self.read(file):
            self.write(file)

        if drate:
            self._drate = drate

        self.set_rate(self._drate)

    def set_rate(self, drate):
        """
        Set rate

        drate = Download rate (KB)
        """
        self._drate = drate
        self.set_args(['-d', str(self._drate), '-s'])

    def read(self, file):
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

    def write(self, file):
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
