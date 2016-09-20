#!/usr/bin/python3
"""
Start "aws" command line
"""

import os
import sys

import awscli.clidriver

if __name__ == '__main__':
    sys.argv[0] = sys.argv[0][:-4]
    sys.argv[0] = os.path.join(os.path.dirname(sys.argv[0]), 'aws')
    sys.exit(awscli.clidriver.main())
