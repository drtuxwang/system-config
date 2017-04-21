#!/usr/bin/python3
"""
Start "jenkins-jobs" command line
"""

import sys

import jenkins_jobs.cmd

if __name__ == '__main__':
    sys.exit(jenkins_jobs.cmd.main())
