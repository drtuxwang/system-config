#!/usr/bin/env python3
"""
Edit multiple files.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        if os.path.isfile('/usr/bin/vim'):
            self._editor = syslib.Command(file='/usr/bin/vim', flags=['-N', '-n', '-u', 'NONE'])
        else:
            self._editor = syslib.Command('vi')
        self._speller = syslib.Command('fspell')

    def get_editor(self):
        """
        Return editor Command class object.
        """
        return self._editor

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_speller(self):
        """
        Return speller Command class object.
        """
        return self._speller

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Edit multiple files.')

        parser.add_argument('files', nargs='+', metavar='file', help='File to edit.')

        self._args = parser.parse_args(args)


class Edit(object):
    """
    Edit class
    """

    def __init__(self, options):
        self._options = options
        files = options.get_files()
        speller = options.get_speller()

        self._edit(files[0])

        while files:
            print('\n' + str(len(files)), 'files =', str(files).replace('u"', '"') + '\n')
            answer = input(' e = Edit   s = Spell check   n = Skip file   q = Quit : ')
            if answer.startswith('e'):
                self._edit(files[0])
            elif answer.startswith('n'):
                files = files[1:]
            elif answer.startswith('q'):
                break
            elif answer.startswith('s'):
                speller.set_args(files[:1])
                speller.run()
                try:
                    os.remove(files[0]+'.bak')
                except OSError:
                    pass

    def _edit(self, file):
        self._options.get_editor().set_args([file])
        sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':' +
                         os.path.abspath(file) + '\007')
        sys.stdout.flush()
        self._options.get_editor().run()
        sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':' + os.getcwd() + '\007')


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
            Edit(options)
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
