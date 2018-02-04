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

import file_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_check_flag(self):
        """
        Return check flag.
        """
        return self._args.check_flag

    def get_create_flag(self):
        """
        Return create flag.
        """
        return self._args.create_flag

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def get_update_file(self):
        """
        Return update file.
        """
        if self._args.update_file:
            return self._args.update_file[0]
        return None

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Calculate checksum using MD5, file size and '
            'file modification time.'
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Recursive into sub-directories.'
        )
        parser.add_argument(
            '-c',
            dest='check_flag',
            action='store_true',
            help='Check checksums against files.'
        )
        parser.add_argument(
            '-f',
            dest='create_flag',
            action='store_true',
            help='Create ".fsum" file for each file.'
        )
        parser.add_argument(
            '-update',
            nargs=1,
            dest='update_file',
            metavar='index.fsum',
            help='Update checksums if file size and date changed.'
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file|file.fsum',
            help='File to checksum or ".fsum" checksum file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

    def _calc(self, options, files):
        for file in files:
            if os.path.isdir(file) and os.path.basename(file) != '...':
                if not os.path.islink(file):
                    if options.get_recursive_flag():
                        try:
                            self._calc(options, sorted([
                                os.path.join(file, x)
                                for x in os.listdir(file)
                            ]))
                        except PermissionError:
                            pass
            elif os.path.isfile(file) and os.path.basename(file) != 'fsum':
                file_stat = file_mod.FileStat(file)
                try:
                    md5sum = self._cache[
                        (file, file_stat.get_size(), file_stat.get_time())]
                except KeyError:
                    md5sum = self._md5sum(file)
                if not md5sum:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + file + '" file.')
                print("{0:s}/{1:010d}/{2:d}  {3:s}".format(
                    md5sum,
                    file_stat.get_size(),
                    file_stat.get_time(),
                    file
                ))
                if options.get_create_flag():
                    try:
                        with open(file + '.fsum', 'w', newline='\n') as ofile:
                            print("{0:s}/{1:010d}/{2:d}  {3:s}".format(
                                md5sum,
                                file_stat.get_size(),
                                file_stat.get_time(),
                                os.path.basename(file)
                            ), file=ofile)
                        file_stat = file_mod.FileStat(file)
                        os.utime(
                            file + '.fsum',
                            (file_stat.get_time(), file_stat.get_time())
                        )
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' + file +
                            '.fsum" file.'
                        )

    def _check(self, files):
        found = []
        nfail = 0
        nmiss = 0

        for fsumfile in files:
            found.append(fsumfile)
            directory = os.path.dirname(fsumfile)
            try:
                with open(fsumfile, errors='replace') as ifile:
                    for line in ifile:
                        line = line.rstrip('\r\n')
                        md5sum, size, mtime, file = self._getfsum(line)
                        file = os.path.join(directory, file)
                        found.append(file)
                        file_stat = file_mod.FileStat(file)
                        try:
                            if not os.path.isfile(file):
                                print(file, '# FAILED open or read')
                                nmiss += 1
                            elif size != file_stat.get_size():
                                print(file, '# FAILED checksize')
                                nfail += 1
                            elif self._md5sum(file) != md5sum:
                                print(file, '# FAILED checksum')
                                nfail += 1
                            elif mtime != file_stat.get_time():
                                print(file, '# FAILED checkdate')
                                nfail += 1
                        except TypeError:
                            raise SystemExit(
                                sys.argv[0] + ': Corrupt "' + fsumfile +
                                '" checksum file.'
                            )
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + fsumfile +
                    '" checksum file.'
                )

        if os.path.join(directory, 'index.fsum') in files:
            for file in self._extra(directory, found):
                print(file, '# EXTRA file found')
        if nmiss > 0:
            print("fsum: Cannot find {0:d} of {1:d} listed files.".format(
                nmiss,
                len(found)
            ))
        if nfail > 0:
            print(
                "fsum: Mismatch in {0:d} of {1:d} computed checksums.".format(
                    nfail,
                    len(found) - nmiss
                )
            )

    def _extra(self, directory, found):
        extra = []
        try:
            if directory:
                files = [
                    os.path.join(directory, x)
                    for x in os.listdir(directory)
                ]
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

    @staticmethod
    def _getfsum(line):
        i = line.find('  ')
        try:
            md5sum, size, mtime = line[:i].split('/')
            size = int(size)
            mtime = int(mtime)
            file = line[i+2:]
            return md5sum, size, mtime, file
        except ValueError:
            return '', -1, -1, ''

    @staticmethod
    def _md5sum(file):
        try:
            with open(file, 'rb') as ifile:
                md5 = hashlib.md5()
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    md5.update(chunk)
        except (OSError, TypeError):
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" file.')
        return md5.hexdigest()

    def run(self):
        """
        Start program
        """
        options = Options()

        if options.get_check_flag():
            self._check(options.get_files())
        else:
            self._cache = {}
            update_file = options.get_update_file()

            if update_file:
                if not os.path.isfile(update_file):
                    raise SystemExit(
                        sys.argv[0] + ': Cannot find "' + update_file +
                        '" checksum file.'
                    )
                try:
                    with open(update_file, errors='replace') as ifile:
                        for line in ifile:
                            try:
                                line = line.rstrip('\r\n')
                                md5sum, size, mtime, file = self._getfsum(line)
                                if file:
                                    self._cache[(file, size, mtime)] = md5sum
                            except IndexError:
                                pass
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + update_file +
                        '" checksum file.'
                    )
            self._calc(options, options.get_files())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
