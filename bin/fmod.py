#!/usr/bin/env python3
"""
Set file access mode.
"""

import argparse
import glob
import os
import re
import signal
import sys

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_fmod(self):
        """
        Return file permission mode.
        """
        return self._fmod

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def get_xmod(self):
        """
        Return executable permission mode.
        """
        return self._xmod

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Set file access mode.')

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Set mod of directories recursively.'
        )
        parser.add_argument(
            '-r',
            dest='mode',
            action='store_const', const='r',
            help='Set read-only permission for user.'
        )
        parser.add_argument(
            '-rg',
            dest='mode',
            action='store_const',
            const='rg',
            help='Set read-only permission for user and group.'
        )
        parser.add_argument(
            '-ra',
            dest='mode',
            action='store_const',
            const='ra',
            help='Set read-only permission for everyone.'
        )
        parser.add_argument(
            '-w',
            dest='mode',
            action='store_const',
            const='w',
            help='Set read-write permission for user.'
        )
        parser.add_argument(
            '-wg',
            dest='mode',
            action='store_const',
            const='wg',
            help='Set read-write permission for user and read for group.'
        )
        parser.add_argument(
            '-wa',
            dest='mode',
            action='store_const',
            const='wa',
            help='Set read-write permission for user and read for others.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File or directory.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        mode = self._args.mode
        if mode == 'r':
            self._xmod = int('500', 8)
            self._fmod = int('400', 8)
        elif mode == 'rg':
            self._xmod = int('550', 8)
            self._fmod = int('440', 8)
        elif mode == 'ra':
            self._xmod = int('555', 8)
            self._fmod = int('444', 8)
        elif mode == 'w':
            self._xmod = int('700', 8)
            self._fmod = int('600', 8)
        elif mode == 'wg':
            self._xmod = int('750', 8)
            self._fmod = int('640', 8)
        elif mode == 'wa':
            self._xmod = int('755', 8)
            self._fmod = int('644', 8)
        else:
            self._xmod = int('755', 8)
            self._fmod = int('644', 8)


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
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

    def _setmod_directory(self, directory):
        try:
            os.chmod(directory, self._xmod)
        except OSError:
            print("Permission denied:", directory + os.sep)
        if self._recursive_flag:
            try:
                self._setmod([
                    os.path.join(directory, x)
                    for x in os.listdir(directory)
                ])
            except PermissionError:
                pass

    def _setmod_file(self, file):
        try:
            try:
                with open(file, 'rb') as ifile:
                    magic = ifile.read(4)
            except OSError:
                os.chmod(file, self._fmod)
                with open(file, 'rb') as ifile:
                    magic = ifile.read(4)

            if (magic.startswith(b'#!') or magic in self._exe_magics or
                    self._is_exe_ext.search(file)):
                os.chmod(file, self._xmod)
            elif self._is_not_exe_ext.search(file):
                os.chmod(file, self._fmod)
            elif os.access(file, os.X_OK):
                os.chmod(file, self._xmod)
            else:
                os.chmod(file, self._fmod)
        except OSError:
            print("Permission denied:", file)

    def _setmod(self, files):
        for file in sorted(files):
            if not os.path.islink(file):
                if os.path.isdir(file):
                    self._setmod_directory(file)
                elif os.path.isfile(file):
                    self._setmod_file(file)
                else:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot find "' + file + '" file.')

    def run(self):
        """
        Start program
        """
        options = Options()

        #   127 ELF,      202 254 186 190   207 250 237 254   206 250 237 254
        #  linux/sunos   macos-x86/x86_64    macos-x86_64        macos-x86
        self._exe_magics = (
            b'\177ELF',
            b'\312\376\272\276',
            b'\317\372\355\376',
            b'\316\372\355\376'
        )
        self._is_exe_ext = re.compile(
            '[.](bat|cmd|com|dll|exe|ms[ip]|psd|sfx|s[olh]|s[ol][.].*|tcl)$',
            re.IGNORECASE
        )
        self._is_not_exe_ext = re.compile(
            '[.](7z|[acfo]|ace|asr|avi|bak|blacklist|bmp|bz2|cpp|crt|css|dat|'
            'deb|diz|doc|docx|f77|f90|gif|gz|h|hlp|htm|html|ico|ini|installed|'
            'ism|iso|jar|java|jpg|jpeg|js|json|key|lic|lib|list|log|mov|'
            'mp[34g]|mpeg|o|obj|od[fgst]|ogg|opt|pdf|png|ppt|pptx|rar|reg|rpm|'
            'swf|tar|txt|url|wsdl|xhtml|xls|xlsx|xml|xs[dl]|xvid|zip)$',
            re.IGNORECASE
        )

        self._recursive_flag = options.get_recursive_flag()
        self._fmod = options.get_fmod()
        self._xmod = options.get_xmod()
        self._files = options.get_files()

        self._setmod(self._files)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
