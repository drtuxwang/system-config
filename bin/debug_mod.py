#!/usr/bin/env python3
"""
Python debugging tools module

Copyright GPL v2: 2015-2016 By Dr Colin Kong

Version 2.1.0 (2016-04-10)
"""

import sys
import time

import jsonpickle

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Dump(object):
    """
    Dump debugging information to stdout or file.
    """

    @staticmethod
    def append(data, file):
        """
        Append data to file.

        data = Bytes
        file = Output file to append
        """
        with open(file, 'ab') as ofile:
            ofile.write(data)

    @classmethod
    def output(cls, message, file=None):
        """
        Show debug message with timestamp.

        message = Message message
        file    = Optional output file to append
        """
        if file:
            cls.append(message.encode() + b'\n', file)
        else:
            print(message)

    @classmethod
    def show(cls, message, file=None):
        """
        Show debug message with timestamp.

        message = Debug message
        file    = Optional output file to append
        """
        cls.output(time.strftime('Debug: %Y-%m-%d-%H:%M:%S: ') + message, file=file)

    @classmethod
    def list(cls, name, obj, indent=4, file=None):
        """
        List object attributes recursively as expanded JSON.

        name   = Name of object (ie "myobject.subobject")
        obj    = Object to dump
        indent = Number of chacracters to indent (default is 4)
        file   = Optional output file to append
        """
        jsonpickle.set_encoder_options('json', indent=indent, sort_keys=True)
        cls.show(name + ' = ' + jsonpickle.encode(obj, unpicklable=False), file=file)
