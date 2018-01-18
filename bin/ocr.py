#!/usr/bin/env python3
"""
Convert image file to text using OCR.
"""

import argparse
import getpass
import glob
import os
import signal
import sys

import command_mod
import config_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_convert(self):
        """
        Return convert Command class object.
        """
        return self._convert

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_tesseract(self):
        """
        Return tesseract Command class object.
        """
        return self._tesseract

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Convert image file to text using OCR.')

        parser.add_argument(
            'files',
            nargs=1,
            metavar='file',
            help='Image file to analyse.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._convert = command_mod.Command('convert', errors='stop')
        self._tesseract = command_mod.Command('tesseract', errors='stop')


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

    def _ocr(self, file, name):
        task = subtask_mod.Task(self._tesseract.get_cmdline() + [file, name])
        task.run(pattern='^Tesseract')
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )

    def run(self):
        """
        Start program
        """
        options = Options()

        self._tesseract = options.get_tesseract()
        convert = options.get_convert()

        tmpfile = os.sep + os.path.join(
            'tmp', 'ocr-' + getpass.getuser() + str(os.getpid()) + '.tif')
        images_extensions = config_mod.Config().get('image_extensions')

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" image file.')
            name, ext = os.path.splitext(file.lower())
            if ext in images_extensions:
                print(
                    'Converting "' + file + '" to "' + name + '.txt' + '"...')
                task = subtask_mod.Task(
                    convert.get_cmdline() + [file, tmpfile])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' +
                        str(task.get_exitcode()) + ' received from "' +
                        task.get_file() + '".'
                    )
                self._ocr(tmpfile, name)
                try:
                    os.remove(tmpfile)
                except OSError:
                    pass
            elif ext in ('tif', 'tiff'):
                print(
                    'Converting "' + file + '" to "' + name + '.txt' + '"...')
                self._ocr(file, name)
            else:
                raise SystemExit(
                    sys.argv[0] + ': Cannot OCR non image file "' +
                    file + '".'
                )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
