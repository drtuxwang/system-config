#!/usr/bin/python3
"""
Start "django-admin" command line
"""

import os
import sys

import django.core.management

if __name__ == '__main__':
    sys.argv[0] = os.path.join(os.path.dirname(sys.argv[0]), 'djanjo-admin')
    sys.exit(django.core.management.execute_from_command_line())
