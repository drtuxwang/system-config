#!/usr/bin/env python3
"""
Check XML file for errors.
"""

import argparse
import glob
import os
import signal
import sys
import xml.sax

import command_mod
import subtask_mod

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

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Check XML file for errors.')

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='View XML data.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='XML/XHTML files.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class XmlDataHandler(xml.sax.ContentHandler):
    """
    XML data handler class
    """

    def __init__(self, view):
        super().__init__()
        self._elements = []
        self._nelement = 0
        self._view_flag = view

    def startElement(self, name, attrs):
        self._nelement += 1
        self._elements.append(name + '(' + str(self._nelement) + ')')
        if self._view_flag:
            for (key, value) in attrs.items():
                print(
                    '.'.join(self._elements + [key]), "='", value, "'", sep='')

    def characters(self, content):
        if self._view_flag:
            print(
                '.'.join(self._elements + ['text']),
                "='" + content.replace('\\', '\\\\').replace('\n', '\\n'),
                "'",
                sep=''
            )

    def endElement(self, name):
        self._elements.pop()


class Main:
    """
    Main class
    """
    xmllint = command_mod.Command('xmllint', errors='stop')

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

    def run(self):
        """
        Start program
        """
        options = Options()

        handler = XmlDataHandler(options.get_view_flag())
        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot open "' + file + '" XML file.')
            task = subtask_mod.Batch(self.xmllint.get_cmdline() + [file])
            task.run()
            if task.has_error():
                for line in task.get_error():
                    print(line, file=sys.stderr)
                continue

            try:
                xml.sax.parse(open(file, errors='replace'), handler)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot parse "' + file + '" XML file.')
            except Exception:
                raise SystemExit(
                    sys.argv[0] + ': Invalid "' + file + '" XML file.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
