#!/usr/bin/env python3
"""
Simple CPython example
"""


def area(height, width):
    """
    Return area
    """
    print("args:", height, width)
    return height * width


print("I am compiled Cython module:", __name__)
