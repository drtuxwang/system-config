#!/usr/bin/env python3
"""
Check XML file for errors.
"""

import argparse
import glob
import http.client
import os
import signal
import sys
import xml.sax

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Check XML file for errors.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='View XML data.')

        parser.add_argument('files', nargs='+', metavar='file', help='XML/XHTML files.')

        self._args = parser.parse_args(args)


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
                print('.'.join(self._elements + [key]), "='", value, "'", sep='')

    def characters(self, text):
        if self._view_flag:
            print('.'.join(self._elements + ['text']), "='" +
                  text.replace('\\', '\\\\').replace('\n', '\\n'), "'", sep='')

    def endElement(self, name):
        self._elements.pop()


class XmlChecker():
    """
    XML checker class
    """

    def __init__(self, options):
        handler = XmlDataHandler(options.get_view_flag())
        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" XML file.')
            try:
                if file.split('.')[-1] in ('htm', 'html', 'xhtml'):
                    # Workaround for bug in xml.sax call to urllib requiring 'http_proxy'
                    self._fixhtml(file)
                    xml.sax.parse(open('xmlcheck.xml', errors='replace'), handler)
                else:
                    xml.sax.parse(open(file, errors='replace'), handler)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot parse "' + file + '" XML file.')
            except http.client.HTTPException:
                raise SystemExit(sys.argv[0] + ': HTTP request failed.')
            except Exception:
                raise SystemExit(sys.argv[0] + ': Invalid "' + file + '" XML file.')
            os.remove('xmlcheck.xml')

    def _fixhtml(self, file):
        try:
            with open(file, errors='replace') as ifile:
                try:
                    with open('xmlcheck.xml', 'w', newline='\n') as ofile:
                        for line in ifile:
                            if line.startswith('<!DOCTYPE html'):
                                ofile.write('\n')
                            else:
                                ofile.write(line.replace('&', '.'))
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "xmlcheck.xml" temporary file.')
        except OSError:
            print(sys.argv[0], ': Cannot parse "', file, '" XML file.', sep='')


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
            XmlChecker(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
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
