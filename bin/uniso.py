#!/usr/bin/env python3
"""
Unpack a portable CD/DVD archive in ISO9660 format.
"""

import argparse
import glob
import logging
import os
import signal
import sys

import command_mod
import logging_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable=invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_images(self):
        """
        Return list of ISO images.
        """
        return self._args.images

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a portable CD/DVD archive in ISO9660 format.')

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show contents of archive.'
        )
        parser.add_argument(
            'images',
            nargs='+',
            metavar='image.iso',
            help='ISO image file.'
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

    @staticmethod
    def _isosize(image, size):
        if size > 734003200:
            logger.info(
                "%s: %4.2f MB (%5.3f salesman's GB)",
                image,
                size/1048576.,
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
                    "your data into multiple images.\n")
            else:
                logger.warning(
                    "This ISO image file does not fit onto "
                    "700MB/80min CD media."
                )
                logger.warning(
                    "==> Please use DVD media or split your "
                    "data into multiple images."
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
                    "'650MB/74min CD media."
                )
                logger.warning("==> Please use 700MB/80min CD media instead.")

    def run(self):
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        view_flag = options.get_view_flag()

        if view_flag:
            archiver = command_mod.Command('7z', args=['l'], errors='stop')
            isoinfo = command_mod.Command(
                'isoinfo',
                args=['-d', '-i'],
                errors='stop'
            )
        else:
            archiver = command_mod.Command(
                '7z',
                args=['x', '-y'],
                errors='stop'
            )

        for image in options.get_images():
            if not os.path.isfile(image):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + image +
                    '" ISO9660 file.'
                )
            task = subtask_mod.Task(archiver.get_cmdline() + [image])
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )
            if view_flag:
                task = subtask_mod.Task(isoinfo.get_cmdline() + [image])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' +
                        str(task.get_exitcode()) + ' received from "' +
                        task.get_file() + '".'
                    )
                self._isosize(image, os.path.getsize(image))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
