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


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

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

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.path.isfile('/usr/bin/vim'):
            self._editor = syslib.Command(file='/usr/bin/vim', flags=['-N', '-n', '-u', 'NONE'])
        else:
            self._editor = syslib.Command('vi')
        self._speller = syslib.Command('fspell')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    def _edit(self, file):
        self._options.get_editor().set_args([file])
        sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':' +
                         os.path.abspath(file) + '\007')
        sys.stdout.flush()
        self._options.get_editor().run()
        sys.stdout.write('\033]0;' + syslib.info.get_hostname() + ':' + os.getcwd() + '\007')

    def run(self):
        """
        Start program
        """
        self._options = Options()
        files = self._options.get_files()
        speller = self._options.get_speller()

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


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
