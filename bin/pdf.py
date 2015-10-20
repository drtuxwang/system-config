#!/usr/bin/env python3
"""
Create PDF from text/images/postscript/PDF files.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")
if __name__ == "__main__":
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import shutil
import signal
import textwrap
import time

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getChars(self):
        """
        Return characters per line.
        """
        return self._args.chars[0]

    def getArchive(self):
        """
        Return PDF archive file.
        """
        return self._archive

    def getFiles(self):
        """
        Return list of files.
        """
        return self._files

    def getPages(self):
        """
        Return pages per page.
        """
        return self._args.pages[0]

    def getPaper(self):
        """
        Return paper size.
        """
        return self._args.paper[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description="Create PDF file from text/images/postscript/PDF files.")

        parser.add_argument("-chars", nargs=1, type=int, default=[100],
                            help="Select characters per line.")
        parser.add_argument("-pages", nargs=1, type=int, choices=[1, 2, 4, 6, 8], default=[1],
                            help="Select pages per page (1, 2, 4, 6, 8).")
        parser.add_argument("-paper", nargs=1, default=["A4"],
                            help="Select paper type. Default is A4.")

        parser.add_argument("files", nargs="+", metavar="file",
                            help='Text/images/postscript/PDF file. A target ".pdf" file can '
                                 'be given as the first file.')

        self._args = parser.parse_args(args)

        if self._args.chars[0] < 0:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "characters per line.")
        if self._args.pages[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "pages per page.")

        if self._args.files[0].endswith(".pdf"):
            self._archive = self._args.files[0]
            self._files = self._args.files[1:]
            if self._archive in self._args.files[1:]:
                raise SystemExit(sys.argv[0] + ": The input and output files must be different.")
        else:
            self._archive = ""
            self._files = self._args.files


class Encode(syslib.Dump):

    def __init__(self, options):
        tmpfile = (os.sep + os.path.join("tmp", "pdf-" + syslib.info.getUsername() + "." +
                                                str(os.getpid())) + "-")
        self._tempfiles = []
        if options.getPages() != 1:
            self._psnup = syslib.Command("psnup", args=["-p" + options.getPaper(), "-m5",
                                         "-" + str(options.getPages())])
        gs = syslib.Command("gs")
        gs.setFlags(["-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=pdfwrite",
                     "-sPAPERSIZE=" + options.getPaper().lower()])
        gs.setArgs(["-sOutputFile=" + options.getArchive(), "-c", ".setpdfwrite"])

        for file in options.getFiles():
            print("Packing", file)
            if not options.getArchive():
                gs.setArgs([
                    "-sOutputFile=" + file.rsplit(".", 1)[0] + ".pdf", "-c", ".setpdfwrite"])
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            ext = file.split(".")[-1].lower()
            if ext == "pdf":
                gs.extendArgs(["-f", file])
            else:
                self._tmpfile = tmpfile + str(len(self._tempfiles) + 1)
                if ext in ("bmp", "gif", "jpg", "jpeg", "png", "pcx", "svg", "tif", "tiff"):
                    self._image(file)
                    self._tempfiles.append(self._tmpfile + ".jpg")
                elif ext in ("ps", "eps"):
                    self._postscript(options, file)
                else:
                    self._text(options, file)
                self._tempfiles.append(self._tmpfile)
                gs.extendArgs(["-f", self._tmpfile])
            if not options.getArchive():
                gs.run()
        if options.getArchive():
            gs.run()

    def __del__(self):
        for file in self._tempfiles:
            try:
                os.remove(file)
            except OSError:
                pass

    def _image(self, file):
        if not hasattr(self, "_convert"):
            self._convert = syslib.Command("convert")
        # Imagemagick low quality method A4 = 595x842, rotate/resize to 545x790 and add 20x20 border
        tmpfile = self._tmpfile + ".png"

        self._convert.setArgs(["-verbose", file, "/dev/null"])
        self._convert.run(filter="^" + file + " ", mode="batch", error2output=True)
        if not self._convert.hasOutput():
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" image file.')
        x, y = self._convert.getOutput()[0].split("+")[0].split()[-1].split("x")
        if int(x) > int(y):
            self._convert.setArgs(["-page", "a4", "-rotate", "90", file, "ps:" + self._tmpfile])
        else:
            self._convert.setArgs(["-page", "a4", file, "ps:" + self._tmpfile])
        self._convert.run(mode="batch")
        if self._convert.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._convert.getExitcode()) +
                             ' received from "' + self._convert.getFile() + '".')
        return 'IMAGE file "' + file + '"'

    def _postscript(self, options, file):
        try:
            with open(file, "rb") as ifile:
                if options.getPages() == 1:
                    try:
                        with open(self._tmpfile, "wb") as ofile:
                            for line in ifile:
                                ofile.write(line.rstrip(b"\r\n\004") + b"\n")
                    except IOError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' + self._tmpfile +
                                         '" temporary file.')
                    self._postscriptFix(self._tmpfile)
                    return 'Postscript file "' + file + '"'
                else:
                    stdin = []
                    for line in ifile:
                        stdin.append(line.rstrip("\r\n" + chr(4)) + "\n")
                    self._psnup.run(mode="batch", stdin=stdin, outputFile=self._tmpfile)
                    if self._psnup.getExitcode():
                        raise SystemExit(sys.argv[0] + ': Error code ' +
                                         str(self._psnup.getExitcode()) + ' received from "' +
                                         self._psnup.getFile() + '".')
                    self._postscriptFix(self._tmpfile)
                    return ('Postscript file "' + file + '" with ' + str(options.getPages()) +
                            ' pages per page')
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" postscript file.')

    def _postscriptFix(self, file):
        scaling = None
        try:
            with open(self._tmpfile, errors="replace") as ifile:
                for line in ifile:
                    if "/a3 setpagesize" in line:
                        scaling = 0.7071
                        break
        except IOError:
            pass
        if scaling:
            with open(file, errors="replace") as ifile:
                with open(file + "-new", "w", newline="\n") as ofile:
                    for line in ifile:
                        line = line.rstrip("\r\n")
                        if line.endswith(" setpagesize"):
                            columns = line.split()
                            columns[2] = "/a4"
                            line = " ".join(columns)
                        elif line.endswith(" scale"):
                            x, y, junk = line.split()
                            line = "{0:6.4f} {1:6.4f} scale".format(float(x)*scaling,
                                                                    float(y)*scaling)
                        print(line, file=ofile)
            os.rename(file + "-new", file)

    def _text(self, options, file):
        if "LANG" in os.environ:
            del os.environ["LANG"]  # Avoids locale problems
        if not hasattr(self, "_a2ps"):
            self._a2ps = syslib.Command("a2ps")
            self._a2ps = syslib.Command("a2ps")
            self._a2ps.setFlags([
                "--media=A4", "--columns=1", "--header=", "--left-footer=", "--footer=",
                "--right-footer=", "--output=-", "--highlight-level=none", "--quiet"])
        chars = options.getChars()

        self._a2ps.setArgs([
            "--portrait", "--chars-per-line=" + str(chars), "--left-title=" +
            time.strftime("%Y-%m-%d-%H:%M:%S"), "--center-title=" + os.path.basename(file)])

        isnotPrintable = re.compile("[\000-\037\200-\277]")
        try:
            with open(file, "rb") as ifile:
                stdin = []
                for line in ifile:
                    line = isnotPrintable.sub(
                        " ", line.decode("utf-8", "replace").rstrip("\r\n\004"))
                    lines = textwrap.wrap(line, chars)
                    if not lines:
                        stdin.append("")
                    else:
                        stdin.extend(lines)
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" text file.')
        if options.getPages() == 1:
            self._a2ps.run(mode="batch", stdin=stdin, outputFile=self._tmpfile)
            if self._a2ps.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(self._a2ps.getExitcode()) +
                                 ' received from "' + self._a2ps.getFile() + '".')
            return 'text file "' + file + '" with ' + str(chars) + ' columns'
        else:
            self._a2ps.run(mode="batch", pipes=[self._psnup], stdin=stdin, outputFile=self._tmpfile)
            if self._a2ps.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(self._a2ps.getExitcode()) +
                                 ' received from "' + self._a2ps.getFile() + '".')
            return ('text file "' + file + '" with ' + str(chars) + ' columns and ' +
                    str(options.getPages()) + ' pages per page')


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Encode(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, "SIGPIPE"):
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


if __name__ == "__main__":
    if "--pydoc" in sys.argv:
        help(__name__)
    else:
        Main()
