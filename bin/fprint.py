#!/usr/bin/env python3
"""
Sends text/images/postscript/PDF files to printer.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.0, < 4.0).")
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

        os.umask(int("077", 8))


    def getChars(self):
        """
        Return characters per line.
        """
        return self._args.chars[0]


    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files


    def getPages(self):
        """
        Return pages per page.
        """
        return self._args.pages[0]


    def getPrinter(self):
        """
        Return printer name.
        """
        return self._printer


    def getViewFlag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag


    def _getDefaultPrinter(self):
        lpstat = syslib.Command("lpstat", args=[ "-d" ], check=False)
        if lpstat.isFound():
            lpstat.run(filter="^system default destination: ", mode="batch")
            if lpstat.hasOutput():
                return lpstat.getOutput()[0].split()[-1]
        return None


    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description="Sends text/images/postscript/PDF to printer.")

        parser.add_argument("-chars", nargs=1, type=int, default=[ 100 ],
                            help="Select characters per line.")
        parser.add_argument("-pages", nargs=1, type=int, choices=[ 1, 2, 4, 6, 8 ], default=[ 1 ],
                            help="Select pages per page (1, 2, 4, 6, 8).")
        parser.add_argument("-paper", nargs=1, default=[ "A4" ],
                            help="Select paper type. Default is A4.")
        parser.add_argument("-printer", nargs=1, help="Select printer name.")
        parser.add_argument("-v", dest="viewFlag", action="store_true",
                            help="Select view instead of priiting.")

        parser.add_argument("files", nargs="+", metavar="file",
                            help="Text/images/postscript/PDF file.")

        self._args = parser.parse_args(args)

        if self._args.chars[0] < 0:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "characters per line.")
        if self._args.pages[0] < 1:
            raise SystemExit(sys.argv[0] + ": You must specific a positive integer for "
                             "pages per page.")

        if self._args.printer:
            self._printer = self._args.printer[0]
        else:
            self._printer = self._getDefaultPrinter()
            if not self._printer:
                raise SystemExit(sys.argv[0] + ": Cannot detect default printer.")


class Print(syslib.Dump):


    def __init__(self, options):
        self._tmpfile = os.sep + os.path.join("tmp",
                "fprint-" + syslib.info.getUsername() + "." + str(os.getpid()))
        if options.getViewFlag():
            evince = syslib.Command("evince")
        else:
            lp = syslib.Command("lp", flags=[ "-o", "number-up=" + str(options.getPages()),
                                              "-d", options.getPrinter() ])

        for file in options.getFiles():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            ext = file.split(".")[-1].lower()
            if ext in ( "bmp", "gif", "jpg", "jpeg", "png", "pcx", "svg", "tif", "tiff" ):
                message = self._image(file)
            elif ext == "pdf":
                message = self._pdf(file)
            elif ext in ( "ps", "eps" ):
                message = self._postscript(options, file)
            else:
                message = self._text(options, file)
            if options.getViewFlag():
                print("Spooling", message, "to printer previewer")
                evince.setArgs([ self._tmpfile ])
                evince.run()
            else:
                print('Spooling ', message, ' to printer "', options.getPrinter(), '"', sep="")
                lp.setArgs([ self._tmpfile ])
                lp.run()
                if lp.getExitcode():
                    raise SystemExit(sys.argv[0] + ': Error code ' + str(lp.getExitcode()) +
                                     ' received from "' + lp.getFile() + '".')
            os.remove(self._tmpfile)


    def _image(self, file):
        if not hasattr(self, "_convert"):
           self._convert = syslib.Command("convert")

        self._convert.setArgs([ "-verbose", file, "/dev/null" ])
        self._convert.run(filter="^" + file + " ", mode="batch", error2output=True)
        if not self._convert.hasOutput():
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" image file.')
        x, y = self._convert.getOutput()[0].split("+")[0].split()[-1].split("x")

        if int(x) > int(y):
            self._convert.setArgs([ "-page", "a4", "-bordercolor", "white", "-border", "40x40",
                                    "-rotate", "90" ])
        else:
            self._convert.setArgs([ "-page", "a4", "-bordercolor", "white", "-border", "40x40" ])
        self._convert.extendArgs([ file, "ps:" + self._tmpfile ])
        self._convert.run(mode="batch")
        if self._convert.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._convert.getExitcode()) +
                                           ' received from "' + self._convert.getFile() + '".')

        return 'IMAGE file "' + file + '"'


    def _pdf(self, file):
        gs = syslib.Command("gs")
        gs.setFlags([ "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER", "-sDEVICE=pswrite",
                      "-sPAPERSIZE=a4", "-r300x300" ])
        gs.setArgs([ "-sOutputFile=" + self._tmpfile, "-c", "save", "pop", "-f", file ])
        gs.run(mode="batch")
        if gs.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(gs.getExitcode()) +
                             ' received from "' + gs.getFile() + '".')
        self._postscriptFix(self._tmpfile)
        return 'PDF file "' + file + '"'


    def _postscript(self, options, file):
        try:
            with open(file, "rb") as ifile:
                try:
                    with open(self._tmpfile, "wb") as ofile:
                        for line in ifile:
                            ofile.write(line.rstrip(b"\r\n\004") + b"\n")
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                     self._tmpfile + '" temporary file.')
                self._postscriptFix(self._tmpfile)
                return 'Postscript file "' + file + '"'
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
                            line = "{0:6.4f} {1:6.4f} scale".format(
                                    float(x)*scaling, float(y)*scaling)
                        print(line, file=ofile)
            os.rename(file + "-new", file)


    def _text(self, options, file):
        if "LANG" in os.environ.keys():
            del os.environ["LANG"] # Avoids locale problems
        if not hasattr(self, "_a2ps"):
            self._a2ps = syslib.Command("a2ps")
            self._a2ps = syslib.Command("a2ps")
            self._a2ps.setFlags([ "--media=A4", "--columns=1", "--header=", "--left-footer=",
                                  "--footer=", "--right-footer=", "--output=-",
                                  "--highlight-level=none", "--quiet" ])
        chars = options.getChars()

        self._a2ps.setArgs([ "--portrait", "--chars-per-line=" + str(chars),
                             "--left-title=" + time.strftime("%Y-%m-%d-%H:%M:%S"),
                             "--center-title=" + os.path.basename(file) ])

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
        self._a2ps.run(mode="batch", stdin=stdin, outputFile=self._tmpfile)
        if self._a2ps.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._a2ps.getExitcode()) +
                             ' received from "' + self._a2ps.getFile() + '".')
        return 'text file "' + file + '" with ' + str(chars) + ' columns'


class Main:

    def __init__(self):
        self._signals()
        if os.name == "nt":
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Print(options)
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
            files = glob.glob(arg) # Fixes Windows globbing bug
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
