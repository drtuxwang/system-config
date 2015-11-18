#!/usr/bin/env python3
"""
Copy all files/directory inside a directory into mirror directory.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import shutil
import signal
import time

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getMirrors(self):
        """
        Return list of mirroring directory pair tuples.
        """
        return self._mirrors

    def getRemoveFlag(self):
        """
        Return remove flag.
        """
        return self._args.removeFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Copy all files/directory inside a directory into mirror directory.')

        parser.add_argument('-rm', dest='removeFlag', action='store_true',
                            help='Delete obsolete files in target directory.')

        parser.add_argument('directories', nargs='+', metavar='sourceDir targetDir',
                            help='Source and target directory pairs.')

        self._args = parser.parse_args(args)

        directories = self._args.directories
        if len(directories) % 2:
            raise SystemExit(sys.argv[0] + ': Source and target directory pair has missing '
                                           'target directory.')
        self._mirrors = []
        for i in range(0, len(directories), 2):
            if not os.path.isdir(directories[i]):
                raise SystemExit(
                    sys.argv[0] + ': Source directory "' + directories[i] + '" does not exist.')
            self._mirrors.append([directories[i], directories[i+1]])


class Mirror:

    def __init__(self, options):
        self._size = 0
        self._start = int(time.time())
        self._options = options
        for mirror in options.getMirrors():
            self._automount(mirror[1], 8)
            self._mirror(mirror[0], mirror[1])
        print('[', self._size, ',', int(time.time()) - self._start, ']', sep='')

    def _automount(self, directory, wait):
        if directory.startswith('/media/'):
            for i in range(wait * 10):
                if os.path.isdir(directory):
                    break
                time.sleep(0.1)

    def _reportOldFiles(self, sourceDir, sourceFiles, targetFiles):
        for targetFile in targetFiles:
            if os.path.join(sourceDir, os.path.basename(targetFile)) not in sourceFiles:
                if os.path.islink(targetFile):
                    print('**WARNING** No source for "' + targetFile + '" link.')
                elif os.path.isdir(targetFile):
                    print('**WARNING** No source for "' + targetFile + '" directory.')
                else:
                    print('**WARNING** No source for "' + targetFile + '" file.')

    def _removeOldFiles(self, sourceDir, sourceFiles, targetFiles):
        for targetFile in targetFiles:
            if os.path.join(sourceDir, os.path.basename(targetFile)) not in sourceFiles:
                if os.path.islink(targetFile):
                    try:
                        os.remove(targetFile)
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot remove "' + targetFile + '" link.')
                elif os.path.isdir(targetFile):
                    print('[', self._size, ',', int(time.time()) - self._start, '] Removing "',
                          targetFile, '" directory.', sep='')
                    try:
                        shutil.rmtree(targetFile)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot remove "' + targetFile + '" directory.')
                else:
                    print('[', self._size, ',', int(time.time()) - self._start, '] Removing "',
                          targetFile, '" file.', sep='')
                    try:
                        os.remove(targetFile)
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot remove "' + targetFile + '" file.')

    def _mirror(self, sourceDir, targetDir):
        try:
            sourceFiles = [os.path.join(sourceDir, x) for x in os.listdir(sourceDir)]
        except PermissionError:
            raise SystemExit(sys.argv[0] + ': Cannot open "' + sourceDir + '" source directory.')
        if os.path.isdir(targetDir):
            try:
                targetFiles = [os.path.join(targetDir, x) for x in os.listdir(targetDir)]
            except PermissionError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot open "' + targetDir + '" target directory.')
        else:
            targetFiles = []
            print('[', self._size, ',', int(time.time()) - self._start, '] Creating "',
                  targetDir, '" directory...', sep='')
            try:
                os.mkdir(targetDir)
                os.chmod(targetDir, syslib.FileStat(sourceDir).getMode())
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + targetDir + '" directory.')

        for sourceFile in sorted(sourceFiles):
            targetFile = os.path.join(targetDir, os.path.basename(sourceFile))
            if os.path.islink(sourceFile):
                sourceLink = os.readlink(sourceFile)
                if (os.path.isfile(targetFile) or os.path.isdir(targetFile) or
                        os.path.islink(targetFile)):
                    if os.path.islink(targetFile):
                        targetLink = os.readlink(targetFile)
                        if targetLink == sourceLink:
                            continue
                    print('[', self._size, ',', int(time.time()) - self._start, '] Updating "',
                          targetFile, '" link...', sep='')
                    try:
                        if os.path.isdir(targetFile) and not os.path.islink(targetFile):
                            shutil.rmtree(targetFile)
                        else:
                            os.remove(targetFile)
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot remove "' + targetFile + '" link.')
                else:
                    print('[', self._size, ',', int(time.time()) - self._start, '] Creating "',
                          targetFile, '" link...', sep='')
                try:
                    os.symlink(sourceLink, targetFile)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + targetFile + '" link.')
            elif os.path.isdir(sourceFile):
                self._mirror(sourceFile, targetFile)
            else:
                if os.path.islink(targetFile):
                    try:
                        os.remove(targetFile)
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot remove "' + targetFile + '" link.')
                elif os.path.isfile(targetFile):
                    sourceFileStat = syslib.FileStat(sourceFile)
                    targetFileStat = syslib.FileStat(targetFile)
                    if sourceFileStat.getSize() == targetFileStat.getSize():
                        # Allow FAT16/FAT32/NTFS 1h daylight saving and 1 sec rounding error
                        if (abs(sourceFileStat.getTime() - targetFileStat.getTime()) in
                                (0, 1, 3599, 3600, 3601)):
                            continue
                    self._size += int((sourceFileStat.getSize() + 1023) / 1024)
                    print('[', self._size, ',', int(time.time()) - self._start, '] Updating "',
                          targetFile, '" file...', sep='')
                else:
                    sourceFileStat = syslib.FileStat(sourceFile)
                    self._size += int((sourceFileStat.getSize() + 1023) / 1024)
                    print('[', self._size, ',', int(time.time()) - self._start, '] Creating "',
                          targetFile, '" file...', sep='')
                try:
                    shutil.copy2(sourceFile, targetFile)
                except IOError as exception:
                    if exception.args != (95, 'Operation not supported'):  # os.listxattr for ACL
                        try:
                            with open(sourceFile):
                                raise SystemExit(
                                    sys.argv[0] + ': Cannot create "' + targetFile + '" file.')
                        except IOError:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot create "' + targetFile + '" file.')
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + sourceFile + '" file.')

        sourceTime = syslib.FileStat(sourceDir).getTime()
        targetTime = syslib.FileStat(targetDir).getTime()
        if sourceTime != targetTime:
            try:
                os.utime(targetDir, (sourceTime, sourceTime))
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot update "' +
                                 targetDir + '" directory modification time.')

        if self._options.getRemoveFlag():
            self._removeOldFiles(sourceDir, sourceFiles, targetFiles)
        else:
            self._reportOldFiles(sourceDir, sourceFiles, targetFiles)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Mirror(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
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
