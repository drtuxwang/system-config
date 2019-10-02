#!/usr/bin/env python3
"""
Copy all files/directory inside a directory into mirror directory.
"""

import argparse
import glob
import logging
import os
import shutil
import signal
import sys
import time

import file_mod
import logging_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")

# pylint: disable = invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable = invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_mirrors(self):
        """
        Return list of mirroring directory pair tuples.
        """
        return self._mirrors

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def get_remove_flag(self):
        """
        Return remove flag.
        """
        return self._args.remove_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Copy all files/directory inside a directory '
            'into mirror directory.'
        )

        parser.add_argument(
            '-R',
            dest='recursive_flag',
            action='store_true',
            help='Mirror directories recursively.'
        )
        parser.add_argument(
            '-rm',
            dest='remove_flag',
            action='store_true',
            help='Delete obsolete files in target directory.'
        )
        parser.add_argument(
            'directories',
            nargs='+',
            metavar='source_dir target_dir',
            help='Source and target directory pairs.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        directories = self._args.directories
        if len(directories) % 2:
            raise SystemExit(
                sys.argv[0] + ': Source and target directory pair has missing '
                'target directory.'
            )
        self._mirrors = []
        for i in range(0, len(directories), 2):
            if not os.path.isdir(directories[i]):
                raise SystemExit(
                    sys.argv[0] + ': Source directory "' + directories[i] +
                    '" does not exist.'
                )
            self._mirrors.append([directories[i], directories[i+1]])


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

    @staticmethod
    def _automount(directory, wait):
        if directory.startswith('/media/'):
            for _ in range(wait * 10):
                if os.path.isdir(directory):
                    break
                time.sleep(0.1)

    @staticmethod
    def _report_old_files(source_dir, source_files, target_files):
        for target_file in target_files:
            if os.path.join(
                    source_dir,
                    os.path.basename(target_file)
            ) not in source_files:
                if os.path.islink(target_file):
                    logger.warning('No source for "%s" link.', target_file)
                elif os.path.isdir(target_file):
                    logger.warning(
                        'No source for "%s" directory.',
                        target_file
                    )
                else:
                    logger.warning('No source for "%s" file.', target_file)

    def _get_stats(self):
        elapsed = time.time() - self._start
        copied = self._size/1024
        return "{0:d}/{1:d}={2:d}".format(
            int(copied),
            int(elapsed),
            int(copied/elapsed)
        )

    def _remove_old_files(self, source_dir, source_files, target_files):
        for target_file in target_files:
            if os.path.join(
                    source_dir,
                    os.path.basename(target_file)
            ) not in source_files:
                if os.path.islink(target_file):
                    try:
                        os.remove(target_file)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot remove "' +
                            target_file + '" link.'
                        )
                elif os.path.isdir(target_file):
                    if self._recursive:
                        logger.warning(
                            '[%s] Removing "%s" directory',
                            self._get_stats(),
                            target_file,
                        )
                        try:
                            shutil.rmtree(target_file)
                        except OSError:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot remove "' +
                                target_file + '" directory.'
                            )
                else:
                    logger.warning(
                        '[%s] Removing "%s" file.',
                        self._get_stats(),
                        target_file,
                    )
                    try:
                        os.remove(target_file)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot remove "' +
                            target_file + '" file.'
                        )

    def _mirror_link(self, source_file, target_file):
        source_link = os.readlink(source_file)
        if (os.path.isfile(target_file) or os.path.isdir(target_file) or
                os.path.islink(target_file)):
            if os.path.islink(target_file):
                target_link = os.readlink(target_file)
                if target_link == source_link:
                    return
            logger.info(
                '[%s] Updating "%s" link.',
                self._get_stats(),
                target_file,
            )
            try:
                if os.path.isdir(target_file) and not (
                        os.path.islink(target_file)):
                    shutil.rmtree(target_file)
                else:
                    os.remove(target_file)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot remove "' +
                    target_file + '" link.'
                )
        else:
            logger.info(
                '[%s] Creating "%s" link.',
                self._get_stats(),
                target_file,
            )
        try:
            os.symlink(source_link, target_file)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + target_file + '" link.')

    def _mirror_file(self, source_file, target_file):
        if os.path.islink(target_file):
            try:
                os.remove(target_file)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot remove "' +
                    target_file + '" link.'
                )
        elif os.path.isfile(target_file):
            source_stat = file_mod.FileStat(source_file)
            target_stat = file_mod.FileStat(target_file)
            if source_stat.get_size() == target_stat.get_size():
                # Allow FAT16/FAT32/NTFS 1h daylight saving
                # and 1 sec rounding error
                if int(
                        abs(source_stat.get_time() - target_stat.get_time())
                ) in (0, 1, 3599, 3600, 3601):
                    if source_stat.get_mode() != target_stat.get_mode():
                        logger.info(
                            '[%s] Updating "%s" permissions.',
                            self._get_stats(),
                            target_file,
                        )
                        try:
                            os.chmod(target_file, source_stat.get_mode())
                        except OSError:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot update "' +
                                target_file + '" permissions.'
                            )
                    return
            logger.info(
                '[%s] Updating "%s" file.',
                self._get_stats(),
                target_file,
            )
        else:
            logger.info(
                '[%s] Creating "%s" file.',
                self._get_stats(),
                target_file,
            )
        self._size += int((os.path.getsize(source_file) + 1023) / 1024)
        try:
            shutil.copy2(source_file, target_file)
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                try:
                    with open(source_file):
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' +
                            target_file + '" file.'
                        )
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' +
                        target_file + '" file.'
                    )

    @staticmethod
    def _mirror_directory_time(source_dir, target_dir):
        source_time = os.path.getmtime(source_dir)
        target_time = os.path.getmtime(target_dir)
        if source_time != target_time:
            try:
                os.utime(target_dir, (source_time, source_time))
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot update "' +
                    target_dir + '" directory modification time.'
                )

    def _mirror(self, source_dir, target_dir):
        try:
            source_files = [
                os.path.join(source_dir, x) for x in os.listdir(source_dir)]
        except (OSError, PermissionError):
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + source_dir +
                '" source directory.'
            )
        if os.path.isdir(target_dir):
            try:
                target_files = [
                    os.path.join(target_dir, x)
                    for x in os.listdir(target_dir)
                ]
            except PermissionError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot open "' + target_dir +
                    '" target directory.'
                )
        else:
            target_files = []
            logger.info(
                '[%s] Creating "%s" directory.',
                self._get_stats(),
                target_dir,
            )
            try:
                if os.path.islink(target_dir):
                    os.remove(target_dir)
                os.mkdir(target_dir)
                os.chmod(
                    target_dir,
                    file_mod.FileStat(source_dir).get_mode()
                )
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + target_dir +
                    '" directory.'
                )

        for source_file in sorted(source_files):
            target_file = os.path.join(
                target_dir,
                os.path.basename(source_file)
            )
            if os.path.islink(source_file):
                self._mirror_link(source_file, target_file)
            elif os.path.isfile(source_file):
                self._mirror_file(source_file, target_file)
            elif os.path.isdir(source_file) and self._recursive:
                self._mirror(source_file, target_file)

        self._mirror_directory_time(source_dir, target_dir)

        if self._options.get_remove_flag():
            self._remove_old_files(source_dir, source_files, target_files)
        else:
            self._report_old_files(source_dir, source_files, target_files)

    def run(self):
        """
        Start program
        """
        self._options = Options()

        self._recursive = self._options.get_recursive_flag()
        self._size = 0
        self._start = int(time.time())
        for mirror in self._options.get_mirrors():
            self._automount(mirror[1], 8)
            self._mirror(mirror[0], mirror[1])
        logger.info('[%s] Finished!', self._get_stats())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
