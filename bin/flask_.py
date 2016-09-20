#!/usr/bin/python3
"""
Start "flask" command line
"""

import os
import sys

import flask.cli

if __name__ == '__main__':
    sys.argv[0] = os.path.join(os.path.dirname(sys.argv[0]), 'flask')
    sys.exit(flask.cli.main())
