#!/usr/bin/env python3
"""
Setup "simple.egg" example
"""

from setuptools import setup

setup(
    name='simple',
    version='1.0',
    description='Simple Egg Example!',
    author='Colin Kong',
    author_email='hob4bit@googlemail.com',
    url='https://github.com/drtuxwang/system-config',
    packages=['hello'],
    long_description="Simple Python Egg exmaple that prints hello world!",
    py_modules=[],
    keywords='simple hello world',
    license='GPL',
    install_requires=[
        'setuptools',
    ],
)
