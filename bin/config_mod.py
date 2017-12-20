#!/usr/bin/env python3
"""
Python configuration module (uses "config_mod.yaml")

Copyright GPL v2: 2017 By Dr Colin Kong
"""

import os
import sys

import yaml

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")

RELEASE = '1.0.2'
VERSION = 20171220


class Config(object):
    """
    This class deals with "config_mod.yml" configuration file.
    """
    def __init__(self):
        file = os.path.join(os.path.dirname(__file__), 'config_mod.yml')
        with open(file) as ifile:
            mappings = yaml.load(ifile)
        self._apps = mappings.get('apps', {})
        self._bindings = mappings.get('bindings', {})
        self._parameters = mappings.get('parameters', {})

    def get(self, parameter):
        """
        Return parameter or None
        """
        return self._parameters.get(parameter)

    def get_app(self, app_name, view=False):
        """
        Return (command, daemon_flag) or None
        """
        app = self._apps.get(app_name)
        if app_name:
            command = app['command']
            if view and 'view_flag' in app:
                command.append(app['view_flag'])
            daemon = app.get('daemon') is True
            return command, daemon

        return None

    def get_open_app(self, extension):
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(extension, {}).get('open')
        if app_name:
            return self.get_app(app_name)

        return None

    def get_view_app(self, extension):
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(extension, {}).get('view')
        if app_name:
            return self.get_app(app_name, view=True)

        return None


if __name__ == '__main__':
    help(__name__)
