#!/usr/bin/env python3
"""
Python network handling utility module

Copyright GPL v2: 2015-2016 By Dr Colin Kong

Version 2.0.0 (2016-02-08)
"""

import json
import os
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Shaper(syslib.Command):
    """
    Shape network traffic class
    """

    def __init__(self, drate=None):
        super().__init__('trickle', check=False)

        self._drate = 512
        if 'HOME' in os.environ:
            file = os.path.join(os.environ['HOME'], '.config', 'netnice.json')
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
                    self._drate = data['netnice']['download']
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
            'netnice': {
                'download': self._drate
            }
        }
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(data, indent=4, sort_keys=True), file=ofile)
        except OSError:
            pass


if __name__ == '__main__':
    help(__name__)
