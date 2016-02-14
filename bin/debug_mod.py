#!/usr/bin/env python3
"""
Python debugging tools module

Copyright GPL v2: 2015-2016 By Dr Colin Kong

Version 2.0.0 (2016-02-08)
"""

import sys

import jsonpickle

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Dump(object):
    """
    This class dumps object attributes recursively.
    """

    @staticmethod
    def _print(name, obj, indent=4):
        jsonpickle.set_encoder_options('json', indent=indent, sort_keys=True)
        print('"' + name, '": ', jsonpickle.encode(obj, unpicklable=False))

    @classmethod
    def show(cls, name, obj):
        """
        Dump object attributes recursively as compact JSON.

        name = Name of object (ie "myobject.subobject")
        obj  = Object to dump
        """
        cls._print(name, obj, indent=None)

    @classmethod
    def list(cls, name, obj):
        """
        List object attributes recursively as expanded JSON.

        name = Name of object (ie "myobject.subobject")
        obj  = Object to dump
        """
        cls._print(name, obj)


if __name__ == '__main__':
    help(__name__)
