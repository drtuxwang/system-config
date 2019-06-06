#!/usr/bin/env python3
"""
Make a portable CD/DVD archive in ISO9660 format.
"""

import argparse
import glob
import hashlib
import logging
import re
import os
import signal
import sys

import command_mod
import file_mod
import logging_mod
import subtask_mod

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

    def get_directory(self):
        """
        Return directory.
        """
        return self._args.directory[0]

    def get_genisoimage(self):
        """
        Return genisoimage Command class object.
        """
        return self._genisoimage

    def get_image(self):
        """
        Return ISO image location.
        """
        return self._image

    def get_isoinfo(self):
        """
        Return isoinfo Command class object.
        """
        return self._isoinfo

    def get_md5_flag(self):
        """
        Return md5sum flag.
        """
        return self._args.md5_flag

    def get_volume(self):
        """
        Return volume name.
        """
        return self._args.volume[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Make a portable CD/DVD archive in ISO9660 format.')

        parser.add_argument(
            '-f',
            dest='follow_flag',
            action='store_true',
            help='Follow symbolic links.'
        )
        parser.add_argument(
            '-md5',
            dest='md5_flag',
            action='store_true',
            help='Create MD5 check sum of ISO image file.'
        )
        parser.add_argument('volume', nargs=1, help='ISO file volume name.')
        parser.add_argument(
            'directory',
            nargs=1,
            help='Directory containing files.'
        )
        parser.add_argument(
            'image',
            nargs='?',
            metavar='image.iso',
            help='Optional image file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._genisoimage = command_mod.Command('genisoimage', errors='stop')
        task = subtask_mod.Batch(
            self._genisoimage.get_cmdline() + ['-version'])
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )
        self._genisoimage.set_args([
            '-iso-level',
            '3',
            '-joliet-long',
            '-rational-rock',
            '-appid',
            'GENISOIMAGE-' + task.get_output()[0].split()[1]
        ])
        if self._args.follow_flag:
            self._genisoimage.append_arg('-follow-links')

        self._isoinfo = command_mod.Command('isoinfo', errors='stop')

        if not os.path.isdir(self._args.directory[0]):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.directory[0] +
                '" directory.'
            )
        if self._args.image:
            self._image = self._args.image
        else:
            self._image = self._args.volume[0] + '.iso'


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

    def _bootimg(self, options):
        files = (
            glob.glob(os.path.join(options.get_directory(), '*.img')) +
            glob.glob(os.path.join(options.get_directory(), '*.bin')) +
            glob.glob(os.path.join(
                options.get_directory(),
                'isolinux',
                '*.bin'
            ))
        )
        if files:
            bootimg = file_mod.FileUtil.newest(files)
            print('Adding Eltorito boot image "' + bootimg + '"...')
            if 'isolinux' in bootimg:
                self._genisoimage.extend_args([
                    '-eltorito-boot',
                    os.path.join('isolinux', os.path.basename(bootimg)),
                    '-no-emul-boot',
                    '-boot-info-table'
                ])
            elif os.path.getsize(bootimg) == 2048:
                self._genisoimage.extend_args([
                    '-eltorito-boot',
                    os.path.basename(bootimg),
                    '-no-emul-boot',
                    '-boot-load-size',
                    '4',
                    '-hide',
                    'boot.catalog'
                ])
            else:
                self._genisoimage.extend_args([
                    '-eltorito-boot',
                    os.path.basename(bootimg),
                    '-hide',
                    'boot.catalog'
                ])

    @staticmethod
    def _isosize(image, size):
        if size > 734003200:
            logger.info(
                "%s: %4.2f MB (%5.3f salesman's GB)",
                image, size/1048576.,
                size/1000000000.,
            )
            if size > 9400000000:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "9.4GB/240min Duel Layer DVD media."
                )
                logger.warning(
                    "==> Please split your data into multiple images."
                )
            elif size > 4700000000:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "4.7GB/120min DVD media."
                )
                logger.warning(
                    "==> Please use Duel Layer DVD media or split "
                    "your data into multiple images."
                )
            else:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "700MB/80min CD media."
                )
                logger.warning(
                    "==> Please use DVD media or split your data "
                    "into multiple images."
                )
            print("")
        else:
            minutes, remainder = divmod(size, 734003200 / 80)
            seconds = remainder * 4800 / 734003200.
            logger.info(
                "%s: %4.2f MB (%.0f min %05.2f sec)",
                image,
                size/1048576.,
                minutes,
                seconds,
            )
            if size > 681574400:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "650MB/74min CD media."
                )
                logger.warning("==> Please use 700MB/80min CD media instead.")

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
            return ''
        return md5.hexdigest()

    def _windisk(self, options):
        if os.name == 'nt':
            self._genisoimage.extend_args(['-file-mode', '444'])
        else:
            command = command_mod.Command(
                'df',
                args=[options.get_directory()],
                errors='ignore'
            )
            mount = command_mod.Command('mount', errors='ignore')
            if command.is_found() and mount.is_found():
                task = subtask_mod.Batch(command.get_cmdline())
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' +
                        str(task.get_exitcode()) + ' received from "' +
                        task.get_file() + '".'
                    )
                if len(task.get_output()) > 1:
                    task2 = subtask_mod.Batch(mount.get_cmdline())
                    task2.run(
                        pattern='^' + task.get_output()[1].split()[0] +
                        ' .* (fuseblk|vfat|ntfs) '
                    )
                    if task2.has_output():
                        print(
                            "Using mode 444 for all plain files (" +
                            task2.get_output()[0].split()[4] +
                            " disk detected)..."
                        )
                        self._genisoimage.extend_args(['-file-mode', '444'])

    def run(self):
        """
        Start program
        """
        options = Options()

        image = options.get_image()

        logger.info("Creating portable CD/DVD image file: %s", image)
        logger.info("Adding ISO9660 Level 3 standard file system")
        logger.info("Adding ROCK RIDGE extensions for UNIX file system")
        logger.info(
            "Adding JOLIET long extensions for Microsoft Windows FAT32 "
            "file system"
        )
        logger.info("Adding individual files shared by all three file systems")
        logger.info(
            "==> Directory and file names limit is  31 characters for ISO9660."
        )
        logger.info(
            "==> Directory and file names limit is 255 "
            "characters for ROCK RIDGE."
        )
        logger.info(
            "==> Directory and file names limit is 103 characters for JOLIET."
        )

        self._genisoimage = options.get_genisoimage()
        self._windisk(options)
        self._bootimg(options)
        self._genisoimage.extend_args([
            '-volid', re.sub(r'[^\w,.+-]', '_', options.get_volume())[:32],
            '-o', image, options.get_directory()])
        task = subtask_mod.Task(self._genisoimage.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )

        if os.path.isfile(image):
            print()
            isoinfo = options.get_isoinfo()
            isoinfo.set_args(['-d', '-i', image])
            task = subtask_mod.Task(isoinfo.get_cmdline())
            task.run(pattern=' id: $')
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )
            self._isosize(image, os.path.getsize(image))
            if options.get_md5_flag():
                print("Creating MD5 check sum of ISO file.")
                md5sum = self._md5sum(image)
                if not md5sum:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + image + '" file.')
                print(md5sum, image, sep='  ')
                try:
                    if image.endswith('.iso'):
                        with open(
                                image[:-4] + '.md5', 'w', newline='\n'
                        ) as ofile:
                            print(md5sum + '  ' + image, file=ofile)
                    else:
                        with open(
                                image + '.md5', 'w', newline='\n'
                        ) as ofile:
                            print(md5sum + '  ' + image, file=ofile)
                except OSError:
                    return


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
