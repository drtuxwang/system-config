#!/usr/bin/env python3
"""
Desktop environment module
"""

import os
import sys

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Desktop(object):
    """
    Desktop class
    """

    def __init__(self):
        self._type = None

    def _detect_xfce(self, keys):
        if 'XDG_MENU_PREFIX' in keys and os.environ['XDG_MENU_PREFIX'] == 'xfce-':
            return 'xfce'
        elif 'XDG_CURRENT_DESKTOP' in keys and os.environ['XDG_CURRENT_DESKTOP'] == 'XFCE':
            return 'xfce'
        elif 'XDG_DATA_DIRS' in keys and '/xfce' in os.environ['XDG_DATA_DIRS']:
            return 'xfce'
        return None

    def _detect_gnome(self, keys):
        if 'DESKTOP_SESSION' in keys and 'gnome' in os.environ['DESKTOP_SESSION']:
            return 'gnome'
        elif 'GNOME_DESKTOP_SESSION_ID' in keys:
            return 'gnome'
        return None

    def _detect_kde(self, keys):
        if 'DESKTOP_SESSION' in keys and 'kde' in os.environ['DESKTOP_SESSION']:
            return 'kde'
        return None

    def detect(self):
        """
        Detect desktop type
        """
        if not self._type:
            keys = os.environ.keys()
            self._type = 'Unknown'
            for method in (self._detect_xfce, self._detect_gnome, self._detect_kde):
                self._type = method(keys)
                if self._type:
                    break
        return self._type


if __name__ == '__main__':
    help(__name__)
