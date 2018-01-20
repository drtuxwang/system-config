#!/usr/bin/env python3
"""
Simple package example
"""

from pkg_resources import require
require('simple')
# pylint: disable = wrong-import-position
import hello.message

hello.message.show()
