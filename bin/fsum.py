#!/usr/bin/env python3
"""
Calculate checksum using MD5, file size and file modification time.
"""

import argparse
import glob
import hashlib
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

    def get_check_flag(self):
        """
        Return check flag.
        """
        return self._args.checkFlag

    def get_create_flag(self):
        """
        Return create flag.
        """
        return self._args.createFlag

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursiveFlag

    def get_update_file(self):
        """
        Return update file.
        """
        if self._args.updateFile:
            return self._args.updateFile[0]
        else:
            return None

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Calculate checksum using MD5, file size and file modification time.')

        parser.add_argument('-R', dest='recursiveFlag', action='store_true',
                            help='Recursive into sub-directories.')
        parser.add_argument('-c', dest='checkFlag', action='store_true',
                            help='Check checksums against files.')
        parser.add_argument('-f', dest='createFlag', action='store_true',
                            help='Create ".fsum" file for each file.')
        parser.add_argument('-update', nargs=1, dest='updateFile', metavar='index.fsum',
                            help='Update checksums if file size and date changed.')

        parser.add_argument('files', nargs='*', metavar='file|file.fsum',
                            help='File to checksum or ".fsum" checksum file.')

        self._args = parser.parse_args(args)


class Checksum(object):
    """
    Check sum class
    """

    def __init__(self, options):
        if options.get_check_flag():
            self._check(options.get_files())
        else:
            self._cache = {}
            updateFile = options.get_update_file()

            if updateFile:
                if not os.path.isfile(updateFile):
                    raise SystemExit(
                        sys.argv[0] + ': Cannot find "' + updateFile + '" checksum file.')
                try:
                    with open(updateFile, errors='replace') as ifile:
                        for line in ifile:
                            try:
                                line = line.rstrip('\r\n')
                                md5sum, size, mtime, file = self._getfsum(line)
                                if file:
                                    self._cache[(file, size, mtime)] = md5sum
                            except IndexError:
                                pass
                except IOError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + updateFile + '" checksum file.')
            self._calc(options, options.get_files())

    def _calc(self, options, files):
        for file in files:
            if os.path.isdir(file):
                if not os.path.islink(file):
                    if options.get_recursive_flag():
                        try:
                            self._calc(options,
                                       sorted([os.path.join(file, x) for x in os.listdir(file)]))
                        except PermissionError:
                            pass
            elif os.path.isfile(file) and not file.endswith('..fsum'):
                fileStat = syslib.FileStat(file)
                try:
                    md5sum = self._cache[(file, fileStat.get_size(), fileStat.get_time())]
                except KeyError:
                    md5sum = self._md5sum(file)
                if not md5sum:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
                print('{0:s}/{1:010d}/{2:d}  {3:s}'.format(md5sum, fileStat.get_size(),
                                                           fileStat.get_time(), file))
                if options.get_create_flag():
                    try:
                        with open(file + '.fsum', 'w', newline='\n') as ofile:
                            print('{0:s}/{1:010d}/{2:d}  {3:s}'.format(md5sum, fileStat.get_size(),
                                  fileStat.get_time(), os.path.basename(file)), file=ofile)
                        fileStat = syslib.FileStat(file)
                        os.utime(file + '.fsum', (fileStat.get_time(), fileStat.get_time()))
                    except (IOError, OSError):
                        raise SystemExit(sys.argv[0] + ': Cannot create "' + file + '.fsum" file.')

    def _check(self, files):
        found = []
        nfiles = 0
        nfail = 0
        nmiss = 0

        for fsumfile in files:
            found.append(fsumfile)
            if not os.path.isfile(fsumfile):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + fsumfile + '" checksum file.')
            directory = os.path.dirname(fsumfile)
            try:
                with open(fsumfile, errors='replace') as ifile:
                    for line in ifile:
                        line = line.rstrip('\r\n')
                        md5sum, size, mtime, file = self._getfsum(line)
                        if file:
                            file = os.path.join(directory, file)
                            found.append(file)
                            nfiles += 1
                            fileStat = syslib.FileStat(file)
                            try:
                                if not os.path.isfile(file):
                                    print(file, '# FAILED open or read')
                                    nmiss += 1
                                elif size != fileStat.get_size():
                                    print(file, '# FAILED checksize')
                                    nfail += 1
                                elif self._md5sum(file) != md5sum:
                                    print(file, '# FAILED checksum')
                                    nfail += 1
                                elif mtime != fileStat.get_time():
                                    print(file, '# FAILED checkdate')
                                    nfail += 1
                            except TypeError:
                                raise SystemExit(
                                    sys.argv[0] + ': Corrupt "' + fsumfile + '" checksum file.')
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + fsumfile + '" checksum file.')

        if os.path.join(directory, 'index.fsum') in files:
            for file in self._extra(directory, found):
                print(file, '# EXTRA file found')
        if nmiss > 0:
            print('fsum: Cannot find', nmiss, 'of', nfiles, 'listed files.')
        if nfail > 0:
            print('fsum: Mismatch in', nfail, 'of', nfiles - nmiss, 'computed checksums.')

    def _extra(self, directory, found):
        extra = []
        try:
            if directory:
                files = [os.path.join(directory, x) for x in os.listdir(directory)]
            else:
                files = [os.path.join(directory, x) for x in os.listdir()]
        except PermissionError:
            pass
        else:
            for file in files:
                if os.path.isdir(file):
                    if not os.path.islink(file):
                        extra.extend(self._extra(file, found))
                elif file not in found:
                    if not file.endswith('..fsum'):
                        extra.append(file)
        return extra

    def _getfsum(self, line):
        i = line.find('  ')
        try:
            md5sum, size, mtime = line[:i].split('/')
            size = int(size)
            mtime = int(mtime)
            file = line[i+2:]
            return (md5sum, size, mtime, file)
        except ValueError:
            return ('', -1, -1, '')

    def _md5sum(self, file):
        try:
            with open(file, 'rb') as ifile:
                md5 = hashlib.md5()
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    md5.update(chunk)
        except (IOError, TypeError):
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
        return md5.hexdigest()


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
            Checksum(options)
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
