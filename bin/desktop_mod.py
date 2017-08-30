#!/usr/bin/env python3
"""
Python X-windows desktop module

Copyright GPL v2: 2013-2017 By Dr Colin Kong
"""

import functools
import os
import sys

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")

RELEASE = '2.1.0'
VERSION = 20170830


class Desktop(object):
    """
    Desktop class
    """

    @staticmethod
    def has_xfce(guess=True):
        """
        Return true if running XFCE
        """
        if os.environ.get('XDG_MENU_PREFIX', '').startswith('xfce-'):
            return True
        elif os.environ.get('XDG_CURRENT_DESKTOP') == 'XFCE':
            return True
        elif '/xfce' in os.environ.get('XDG_DATA_DIRS', ''):
            return True
        elif (
                guess and
                os.path.isfile('/usr/bin/thunar') and
                os.path.isfile('/usr/bin/xfce4-terminal')
        ):
            return True
        return False

    @staticmethod
    def has_gnome():
        """
        Return true if running Gnome
        """
        keys = os.environ.keys()
        if 'gnome' in os.environ.get('DESKTOP_SESSION', ''):
            return True
        elif 'GNOME_DESKTOP_SESSION_ID' in keys:
            return True
        return False

    @staticmethod
    def has_kde():
        """
        Return true if running KDE
        """
        if 'kde' in os.environ.get('DESKTOP_SESSION', ''):
            return True
        return False

    @staticmethod
    def has_macos():
        """
        Return true if running MacOS desktop
        """
        if os.name == 'posix' and os.uname()[0] == 'Darwin':
            return True
        return False

    @classmethod
    @functools.lru_cache(maxsize=1)
    def detect(cls):
        """
        Return desktop name (xfce, gnome, kde or Unknown)
        """
        name = 'Unknown'
        if 'DISPLAY' in os.environ:
            if cls.has_macos():
                name = 'macos'
            elif cls.has_xfce():
                name = 'xfce'
            elif cls.has_gnome():
                name = 'gnome'
            elif cls.has_kde():
                name = 'kde'
            elif cls.has_xfce(guess=True):
                name = 'xfce'

        return name


if __name__ == '__main__':
    help(__name__)
