#!/usr/bin/env python3
"""
Wrapper for 'pep8' Python PEP8 compliance checking.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import pep8
import pkg_resources

pep8.MAX_LINE_LENGTH = 100
version = pkg_resources.get_distribution('PEP8').version

if __name__ == "__main__":
    sys.exit(pkg_resources.load_entry_point('pep8=='+version, 'console_scripts', 'pep8')())
