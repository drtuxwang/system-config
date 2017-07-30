#!/usr/bin/python3
"""
Start "youtube-dl" command line
"""

import sys

import youtube_dl

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")

if __name__ == '__main__':
    sys.exit(youtube_dl.main())
