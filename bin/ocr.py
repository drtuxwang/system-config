#!/usr/bin/env python3
"""
Convert image file to text using OCR.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._convert = syslib.Command('convert')
        self._tesseract = syslib.Command('tesseract')

    def getConvert(self):
        """
        Return convert Command class object.
        """
        return self._convert

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getTesseract(self):
        """
        Return tesseract Command class object.
        """
        return self._tesseract

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Convert image file to text using OCR.')

        parser.add_argument('files', nargs=1, metavar='file', help='Image file to analyse.')

        self._args = parser.parse_args(args)


class Ocr:

    def __init__(self, options):
        self._tesseract = options.getTesseract()
        convert = options.getConvert()

        tmpfile = os.sep + os.path.join('tmp', 'ocr-' + syslib.info.getUsername() +
                                        str(os.getpid()) + '.tif')
        for file in options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" image file.')
            ext = file.split('.')[-1].lower()
            name = file.rsplit('.', 1)[0]
            if ext in ('bmp', 'jpg', 'jpeg', 'png', 'pcx'):
                print('Converting "' + file + '" to "' + name + '.txt' + '"...')
                convert.setArgs([file, tmpfile])
                convert.run()
                if convert.getExitcode():
                    raise SystemExit(sys.argv[0] + ': Error code ' + str(convert.getExitcode()) +
                                     ' received from "' + convert.getFile() + '".')
                self._ocr(options, tmpfile, name)
                try:
                    os.remove(tmpfile)
                except OSError:
                    pass
            elif ext in ('tif', 'tiff'):
                print('Converting "' + file + '" to "' + name + '.txt' + '"...')
                self._ocr(options, file, name)
            else:
                raise SystemExit(sys.argv[0] + ': Cannot OCR non image file "' + file + '".')

    def _ocr(self, options, file, name):
        self._tesseract.setArgs([file, name])
        self._tesseract.run(filter='^Tesseract')
        if self._tesseract.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._tesseract.getExitcode()) +
                             ' received from "' + self._tesseract.getFile() + '".')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Ocr(options)
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
