#!/usr/bin/env python3
"""
Look up mail aliases in '.mailrc' file.
"""

import argparse
import glob
import os
import re
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._domain_name = ''
        if 'HOME' in os.environ:
            try:
                with open(os.path.join(os.environ['HOME'], '.address'), errors='replace') as ifile:
                    self._domain_name = ifile.readline().strip().split('@')[-1]
            except OSError:
                pass
        if not self._domain_name:
            domain_name = syslib.Command('domainname')
            domain_name.run(mode='batch')
            if domain_name.has_output():
                self._domain_name = domain_name.get_output()[0]

    def get_aliases(self):
        """
        Return list of aliases.
        """
        return self._args.aliases

    def get_domain_name(self):
        """
        Return domain name.
        """
        return self._domain_name

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Look up mail aliases in ".mailrc" file.')

        parser.add_argument('aliases', nargs='+', metavar='alias', help='E-mail alias.')

        self._args = parser.parse_args(args)


class Address(object):
    """
    Address class
    """

    def __init__(self):
        self._names = []
        self._book = {}
        if 'HOME' in os.environ:
            try:
                with open(os.path.join(os.environ['HOME'], '.mailrc'), errors='replace') as ifile:
                    iscomment = re.compile('^( |\t)*#')
                    for line in ifile:
                        if not iscomment.match(line):
                            if len(line.split()) == 2:
                                name, address = line.strip().split()
                                self._book[name] = address
                                self._names.append(name)
            except OSError:
                pass

    def match(self, domainname, aliases):
        """
        Match address
        """
        addresses = []
        for alias in aliases:
            try:
                is_match = re.compile(alias, re.IGNORECASE)
            except re.error:
                raise SystemExit(sys.argv[0] + ': Invalid regular expression "' + alias + '".')
            if '@' in alias:
                addresses.append(alias)
            else:
                address = alias + '@' + domainname
                for name in self._names:
                    if is_match.search(name):
                        address = self._book[name]
                        break
                addresses.append(address)
        print(','.join(addresses))


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Address().match(options.get_domain_name(), options.get_aliases())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
