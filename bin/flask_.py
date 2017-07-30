#!/usr/bin/python3
"""
Start "flask" command line
"""

import os
import sys

import flask.cli

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")

if __name__ == '__main__':
    sys.argv[0] = os.path.join(os.path.dirname(sys.argv[0]), 'flask')
    sys.exit(flask.cli.main())
