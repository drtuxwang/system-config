#!/usr/bin/env python3
"""
Python debugging module

Copyright GPL v2: 2016 By Dr Colin Kong

Version 1.0.0 (2016-01-24)
"""

import sys

import jsonpickle

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Dump(object):
    """
    This class dumps object attributes recursively.
    """

    def _print(self, name, obj, indent=4):
        jsonpickle.set_encoder_options('json', indent=indent, sort_keys=True)
        print('"' + name, '": ', jsonpickle.encode(obj, unpicklable=False))

    def show(self, name, obj):
        """
        Dump object attributes recursively as compact JSON.

        name = Name of object (ie "myobject.subobject")
        obj  = Object to dump
        """
        self._print(name, obj, indent=None)

    def list(self, name, obj):
        """
        List object attributes recursively as expanded JSON.

        name = Name of object (ie "myobject.subobject")
        obj  = Object to dump
        """
        self._print(name, obj)


if __name__ == '__main__':
    help(__name__)
