#!/usr/bin/env python3
"""
Sends text/images/postscript/PDF files to printer/preview.
"""

import argparse
import getpass
import glob
import os
import re
import shutil
import signal
import sys
import textwrap
import time

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_chars(self):
        """
        Return characters per line.
        """
        return self._args.chars[0]

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_pages(self):
        """
        Return pages per page.
        """
        return self._args.pages[0]

    def get_printer(self):
        """
        Return printer name.
        """
        return self._printer

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    @staticmethod
    def _get_default_printer():
        lpstat = command_mod.Command('lpstat', args=['-d'], errors='ignore')
        if lpstat.is_found():
            task = subtask_mod.Batch(lpstat.get_cmdline())
            task.run(pattern='^system default destination: ')
            if task.has_output():
                return task.get_output()[0].split()[-1]
        return None

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Sends text/images/postscript/PDF to printer.')

        parser.add_argument('-chars', nargs=1, type=int, default=[100],
                            help='Select characters per line.')
        parser.add_argument('-pages', nargs=1, type=int, choices=[1, 2, 4, 6, 8], default=[1],
                            help='Select pages per page (1, 2, 4, 6, 8).')
        parser.add_argument('-paper', nargs=1, default=['A4'],
                            help='Select paper type. Default is A4.')
        parser.add_argument('-printer', nargs=1, help='Select printer name.')
        parser.add_argument('-v', dest='view_flag', action='store_true',
                            help='Select view instead of priiting.')

        parser.add_argument('files', nargs='+', metavar='file',
                            help='Text/images/postscript/PDF file.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        os.umask(int('077', 8))

        if self._args.chars[0] < 0:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'characters per line.')
        if self._args.pages[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'pages per page.')

        if self._args.printer:
            self._printer = self._args.printer[0]
        else:
            self._printer = self._get_default_printer()
            if not self._printer:
                raise SystemExit(sys.argv[0] + ': Cannot detect default printer.')


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

    def _image(self, file):
        convert = command_mod.Command('convert', errors='stop')
        jpeg2ps = command_mod.Command('jpeg2ps', errors='ignore')

        if jpeg2ps.is_found():
            # Old but still most reliable
            convert.set_args([file, self._tmpfile + '.jpg'])
            task = subtask_mod.Batch(convert.get_cmdline())
            task.run()

            jpeg2ps.set_args(['-a', '-p', 'a4', '-o', self._tmpfile, self._tmpfile + '.jpg'])
            task = subtask_mod.Batch(jpeg2ps.get_cmdline())

        else:
            # Image magic is a bit buggy
            convert.set_args(['-verbose', file, '/dev/null'])
            task = subtask_mod.Batch(convert.get_cmdline())
            task.run(pattern='^' + file + ' ', error2output=True)
            if not task.has_output():
                raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" image file.')
            xsize, ysize = task.get_output()[0].split('+')[0].split()[-1].split('x')

            if int(xsize) > int(ysize):
                convert.set_args([
                    '-page', 'a4', '-bordercolor', 'white', '-border', '40x40', '-rotate', '90'])
            else:
                convert.set_args(['-page', 'a4', '-bordercolor', 'white', '-border', '40x40'])
            convert.extend_args([file, 'ps:' + self._tmpfile])
            task = subtask_mod.Batch(convert.get_cmdline())

        task.run()
        if task.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                             ' received from "' + task.get_file() + '".')

        return 'IMAGE file "' + file + '"'

    def _pdf(self, file):
        command = command_mod.Command('gs', errors='stop')
        command.set_args([
            '-q', '-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=pswrite', '-sPAPERSIZE=a4',
            '-r300x300', '-sOutputFile=' + self._tmpfile, '-c', 'save', 'pop', '-f', file])
        task = subtask_mod.Batch(command.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                             ' received from "' + task.get_file() + '".')
        self._postscript_fix(self._tmpfile)
        return 'PDF file "' + file + '"'

    def _postscript(self, file):
        try:
            with open(file, 'rb') as ifile:
                try:
                    with open(self._tmpfile, 'wb') as ofile:
                        for line in ifile:
                            ofile.write(line.rstrip(b'\r\n\004') + b'\n')
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + self._tmpfile + '" temporary file.')
                self._postscript_fix(self._tmpfile)
                return 'Postscript file "' + file + '"'
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" postscript file.')

    def _postscript_fix(self, file):
        scaling = None
        try:
            with open(self._tmpfile, errors='replace') as ifile:
                for line in ifile:
                    if '/a3 setpagesize' in line:
                        scaling = 0.7071
                        break
        except OSError:
            pass

        if scaling:
            with open(file, errors='replace') as ifile:
                with open(file + '-new', 'w', newline='\n') as ofile:
                    for line in ifile:
                        line = line.rstrip('\r\n')
                        if line.endswith(' setpagesize'):
                            columns = line.split()
                            columns[2] = '/a4'
                            line = ' '.join(columns)
                        elif line.endswith(' scale'):
                            xsize, ysize, _ = line.split()
                            line = '{0:6.4f} {1:6.4f} scale'.format(
                                float(xsize)*scaling, float(ysize)*scaling)
                        print(line, file=ofile)
            shutil.move(file + '-new', file)

    def _text(self, options, file):
        if 'LANG' in os.environ:
            del os.environ['LANG']  # Avoids locale problems
        a2ps = command_mod.Command('a2ps', errors='stop')
        # Space in header and footer increase top/bottom margins
        a2ps.set_args(['--media=A4', '--columns=1', '--header= ', '--left-footer=', '--footer= ',
                       '--right-footer=', '--output=-', '--highlight-level=none', '--quiet'])
        chars = options.get_chars()

        a2ps.extend_args(['--portrait', '--chars-per-line=' + str(chars),
                          '--left-title=' + time.strftime('%Y-%m-%d-%H:%M:%S'),
                          '--center-title=' + os.path.basename(file)])

        is_not_printable = re.compile('[\000-\037\200-\277]')
        try:
            with open(file, 'rb') as ifile:
                stdin = []
                for line in ifile:
                    line = is_not_printable.sub(
                        ' ', line.decode('utf-8', 'replace').rstrip('\r\n\004'))
                    lines = textwrap.wrap(line, chars)
                    if not lines:
                        stdin.append('')
                    else:
                        stdin.extend(lines)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" text file.')
        task = subtask_mod.Batch(a2ps.get_cmdline())
        task.run(stdin=stdin, file=self._tmpfile)
        if task.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                             ' received from "' + task.get_file() + '".')
        return 'text file "' + file + '" with ' + str(chars) + ' columns'

    def run(self):
        """
        Start program
        """
        options = Options()

        self._tmpfile = os.sep + os.path.join(
            'tmp', 'fprint-' + getpass.getuser() + '.' + str(os.getpid()))
        if options.get_view_flag():
            evince = command_mod.Command('evince', errors='stop')
        else:
            command = command_mod.Command('lp', errors='stop')
            command.set_args(['-U', 'someone', '-o', 'number-up=' + str(options.get_pages()),
                              '-d', options.get_printer()])

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            ext = file.split('.')[-1].lower()
            if ext in ('bmp', 'gif', 'jpg', 'jpeg', 'png', 'pcx', 'svg', 'tif', 'tiff'):
                message = self._image(file)
            elif ext == 'pdf':
                message = self._pdf(file)
            elif ext in ('ps', 'eps'):
                message = self._postscript(file)
            else:
                message = self._text(options, file)
            if options.get_view_flag():
                print('Spooling', message, 'to printer previewer')
                subtask_mod.Task(evince.get_cmdline() + [self._tmpfile]).run()
            else:
                print('Spooling ', message, ' to printer "', options.get_printer(), '"', sep='')
                task = subtask_mod.Task(command.get_cmdline() + [self._tmpfile])
                task.run()
                if task.get_exitcode():
                    raise SystemExit(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                                     ' received from "' + task.get_file() + '".')
            os.remove(self._tmpfile)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
