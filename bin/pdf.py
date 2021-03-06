#!/usr/bin/env python3
"""
Create PDF from text/images/postscript/PDF files.
"""

import argparse
import glob
import os
import re
import shutil
import signal
import sys
import textwrap
import time

import command_mod
import config_mod
import file_mod
import subtask_mod


class Options:
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

    def get_archive(self):
        """
        Return PDF archive file.
        """
        return self._archive

    def get_files(self):
        """
        Return list of files.
        """
        return self._files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Create PDF file from text/images/'
            'postscript/PDF files.'
        )

        parser.add_argument(
            '-chars',
            nargs=1,
            type=int,
            default=[100],
            help='Select characters per line.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Text/images/postscript/PDF file. A target ".pdf" file can '
            'be given as the first file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.chars[0] < 0:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'characters per line.'
            )

        if self._args.files[0].endswith('.pdf'):
            self._archive = self._args.files[0]
            self._files = self._args.files[1:]
            if self._archive in self._args.files[1:]:
                raise SystemExit(
                    sys.argv[0] +
                    ': The input and output files must be different.'
                )
        else:
            self._archive = ''
            self._files = self._args.files


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            self._tempfiles = []
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

    def __del__(self):
        for file in self._tempfiles:
            try:
                os.remove(file)
            except OSError:
                pass

    def _image(self, file):
        if 'convert' not in self._cache:
            self._cache['convert'] = command_mod.Command(
                'convert',
                errors='stop'
            )
        convert = self._cache['convert']

        task = subtask_mod.Batch(
            convert.get_cmdline() + ['-verbose', file, '/dev/null'])
        task.run(pattern='^' + file + ' ', error2output=True)
        if not task.has_output():
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" image file.')
        xsize, ysize = task.get_output(
            )[0].split('+')[0].split()[-1].split('x')
        cmdline = convert.get_cmdline() + ['-page', 'a4']
        if 'page' not in file:
            cmdline.extend(['-border', '30', '-bordercolor', 'white'])
        if int(xsize) > int(ysize):
            cmdline.extend(['-rotate', '270'])
        cmdline.extend([file, 'pdf:' + self._tmpfile])

        task = subtask_mod.Batch(cmdline)
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )
        return 'IMAGE file "' + file + '"'

    def _postscript(self, file):
        try:
            with open(file, 'rb') as ifile:
                try:
                    with open(self._tmpfile, 'wb') as ofile:
                        for line in ifile:
                            ofile.write(line.rstrip(b"\r\n\004") + b"\n")
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + self._tmpfile +
                        '" temporary file.'
                    ) from exception
                self._postscript_fix(self._tmpfile)
                return 'Postscript file "' + file + '"'
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" postscript file.'
            ) from exception

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
                with open(file + '.part', 'w', newline='\n') as ofile:
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
            shutil.move(file + '.part', file)

    def _text(self, options, file):
        if 'LANG' in os.environ:
            del os.environ['LANG']  # Avoids locale problems
        if 'a2ps' not in self._cache:
            self._cache['a2ps'] = command_mod.Command('a2ps', errors='stop')
            self._cache['a2ps'].set_args([
                '--media=a4',
                '--columns=1',
                '--header=',
                '--left-footer=',
                '--footer=',
                '--right-footer=',
                '--output=-',
                '--highlight-level=none',
                '--quiet'
            ])
        a2ps = self._cache['a2ps']
        chars = options.get_chars()

        a2ps.extend_args([
            '--portrait',
            '--chars-per-line=' + str(chars),
            '--left-title=' + time.strftime('%Y-%m-%d-%H:%M:%S'),
            '--center-title=' + os.path.basename(file)
        ])

        is_not_printable = re.compile('[\000-\037\200-\277]')
        try:
            with open(file, 'rb') as ifile:
                stdin = []
                for line in ifile:
                    line = is_not_printable.sub(
                        ' ',
                        line.decode('utf-8', 'replace').rstrip('\r\n\004')
                    )
                    lines = textwrap.wrap(line, chars)
                    if not lines:
                        stdin.append('')
                    else:
                        stdin.extend(lines)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" text file.'
            ) from exception
        task = subtask_mod.Batch(a2ps.get_cmdline())
        task.run(stdin=stdin, file=self._tmpfile)
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )
        return 'text file "' + file + '" with ' + str(chars) + ' columns'

    def run(self):
        """
        Start program
        """
        options = Options()
        self._cache = {}

        tmpdir = file_mod.FileUtil.tmpdir('.cache')
        tmpfile = os.path.join(tmpdir, 'pdf.tmp' + str(os.getpid()))
        command = command_mod.Command('gs', errors='stop')
        command.set_args([
            '-q',
            '-dNOPAUSE',
            '-dBATCH',
            '-dSAFER',
            '-sDEVICE=pdfwrite',
            '-sPAPERSIZE=a4',
        ])

        images_extensions = config_mod.Config().get('image_extensions')

        args = ['-sOutputFile=' + options.get_archive(), '-c', '.setpdfwrite']
        for file in options.get_files():
            print("Packing", file)
            if not options.get_archive():
                args = [
                    '-sOutputFile=' + file.rsplit('.', 1)[0] + '.pdf',
                    '-c',
                    '.setpdfwrite'
                ]
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            _, ext = os.path.splitext(file.lower())
            if ext == '.pdf':
                args.extend(['-f', file])
            else:
                self._tmpfile = tmpfile + str(len(self._tempfiles) + 1)
                if ext in images_extensions:
                    self._image(file)
                    self._tempfiles.append(self._tmpfile + '.jpg')
                elif ext in ('ps', 'eps'):
                    self._postscript(file)
                else:
                    self._text(options, file)
                self._tempfiles.append(self._tmpfile)
                args.extend(['-f', self._tmpfile])
            if not options.get_archive():
                subtask_mod.Task(command.get_cmdline() + args).run()
        if options.get_archive():
            subtask_mod.Task(command.get_cmdline() + args).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
