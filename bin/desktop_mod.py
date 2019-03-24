#!/usr/bin/env python3
"""
Python X-windows desktop module

Copyright GPL v2: 2013-2019 By Dr Colin Kong
"""

import functools
import getpass
import os
import subprocess
import sys


if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")

RELEASE = '2.3.2'
VERSION = 20190324


class _System:

    @staticmethod
    def is_windows():
        """
        Return True if running on Windows.
        """
        if os.name == 'posix':
            if os.uname()[0].startswith('cygwin'):
                return True
        elif os.name == 'nt':
            return True

        return False

    @staticmethod
    def _locate_program(program):
        for directory in os.environ['PATH'].split(os.pathsep):
            file = os.path.join(directory, program)
            if os.path.isfile(file):
                break
        else:
            return None
        return file

    @classmethod
    def run_program(cls, command):
        """
        Run program in batch mode and return list of lines.
        """
        program = cls._locate_program(command[0])
        if not program:
            return []

        try:
            child = subprocess.Popen(
                [program] + command[1:],
                shell=False,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
        except OSError:
            return []

        lines = []
        while True:
            try:
                line = child.stdout.readline().decode('utf-8', 'replace')
            except (KeyboardInterrupt, OSError):
                break
            if not line:
                break
            lines.append(line.rstrip('\r\n'))
        return lines


class Desktop:
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
        command = ['ps', '-o', 'args', '-u', getpass.getuser()]
        lines = _System.run_program(command)
        names = set([os.path.basename(line.split()[0]) for line in lines])

        if 'xfce4-session' in names:
            return 'xfce'
        if (
                set(['gnome-panel', 'gnome-session', 'gnome-session-binary']) &
                names
        ):
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
            elif not _System.is_windows():
                name = cls.guess()

        return name


if __name__ == '__main__':
    help(__name__)
