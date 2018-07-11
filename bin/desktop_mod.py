#!/usr/bin/env python3
"""
Python X-windows desktop module

Copyright GPL v2: 2013-2018 By Dr Colin Kong
"""

import functools
import getpass
import os
import sys

import psutil


if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")

RELEASE = '2.2.0'
VERSION = 20180711


class Desktop(object):
    """
    Desktop class
    """

    @staticmethod
    def has_xfce():
        """
        Return true if running XFCE
        """
        if os.environ.get('DESKTOP_SESSION') == 'xfce':
            return True
        if os.environ.get('XDG_MENU_PREFIX', '').startswith('xfce-'):
            return True
        if os.environ.get('XDG_CURRENT_DESKTOP') == 'XFCE':
            return True
        if '/xfce' in os.environ.get('XDG_DATA_DIRS', ''):
            return True
        return False

    @staticmethod
    def has_gnome():
        """
        Return true if running Gnome
        """
        if os.environ.get('DESKTOP_SESSION', '') == 'gnome':
            return True
        if 'GNOME_DESKTOP_SESSION_ID' in os.environ.keys():
            return True
        return False

    @staticmethod
    def has_kde():
        """
        Return true if running KDE
        """
        if os.environ.get('DESKTOP_SESSION', '') in ('kde', 'plasma'):
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

    @staticmethod
    def guess():
        """
        Guess desktop based on session user is running. Return name or Unknown.
        """
        username = getpass.getuser()
        names = set([
            process.name()
            for process in psutil.process_iter()
            if process.username() == username
        ])

        if 'xfce4-session' in names:
            return 'xfce'
        if set(['gnome-session', 'gnome-session-binary']) & names:
            return 'gnome'
        if 'startkde' in names:
            return 'kde'

        return 'Unknown'

    @classmethod
    @functools.lru_cache(maxsize=1)
    def detect(cls):
        """
        Return desktop name or Unknown)
        """
        name = 'Unknown'
        if 'DISPLAY' in os.environ:
            if cls.has_xfce():
                name = 'xfce'
            elif cls.has_gnome():
                name = 'gnome'
            elif cls.has_kde():
                name = 'kde'
            if cls.has_macos():
                name = 'macos'
            else:
                name = cls.guess()

        return name


if __name__ == '__main__':
    help(__name__)
