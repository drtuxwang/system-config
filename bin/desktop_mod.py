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

RELEASE = '2.0.4'
VERSION = 20170730


class Desktop(object):
    """
    Desktop class
    """

    @staticmethod
    def has_xfce():
        """
        Return true if running XFCE
        """
        keys = os.environ.keys()
        if ('XDG_MENU_PREFIX' in keys and
                os.environ['XDG_MENU_PREFIX'] == 'xfce-'):
            return True
        elif ('XDG_CURRENT_DESKTOP' in keys and
              os.environ['XDG_CURRENT_DESKTOP'] == 'XFCE'):
            return True
        elif ('XDG_DATA_DIRS' in keys and
              '/xfce' in os.environ['XDG_DATA_DIRS']):
            return True
        return False

    @staticmethod
    def has_gnome():
        """
        Return true if running Gnome
        """
        keys = os.environ.keys()
        if ('DESKTOP_SESSION' in keys and
                'gnome' in os.environ['DESKTOP_SESSION']):
            return True
        elif 'GNOME_DESKTOP_SESSION_ID' in keys:
            return True
        return False

    @staticmethod
    def has_kde():
        """
        Return true if running KDE
        """
        keys = os.environ.keys()
        if ('DESKTOP_SESSION' in keys and
                'kde' in os.environ['DESKTOP_SESSION']):
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
        if cls.has_macos():
            name = 'macos'
        elif cls.has_xfce():
            name = 'xfce'
        elif cls.has_gnome():
            name = 'gnome'
        elif cls.has_kde():
            name = 'kde'
        else:
            name = 'Unknown'

        return name


if __name__ == '__main__':
    help(__name__)
