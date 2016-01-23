#!/usr/bin/env python3
"""
Generate multiple graph files with X/Y plots.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._gnuplot = syslib.Command('gnuplot')

    def get_file(self):
        """
        Return file.
        """
        return self._args.file[0]

    def get_gnuplot(self):
        """
        Return gnuplot Command class object.
        """
        return self._gnuplot

    def get_mode(self):
        """
        Return operation mode.
        """
        return self._args.mode

    def get_xcol(self):
        """
        Return X column.
        """
        return self._args.xcol[0]

    def get_xrange(self):
        """
        Return X range.
        """
        return self._xrange

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Generate multiple graph files with X/Y plots.')

        parser.add_argument('-mode', nargs=1, choices=['l', 'p', 'lp'], default='lp',
                            help='Select lines(l), points(p) or both (lp). Default is lp.')
        parser.add_argument('-xcol', nargs=1, type=int, default=[1],
                            help='Select column number for X-axis.')
        parser.add_argument('-xrange', nargs=1, metavar='n:n', help='Select range for X-axis.')

        parser.add_argument('file', nargs=1, help='Text file containing data.')

        self._args = parser.parse_args(args)

        if self._args.xcol[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'X-axis column number.')

        if self._args.xrange:
            self._xrange = '[' + self._args.xrange[0] + '] '
        else:
            self._xrange = ''


class Graph(object):
    """
    Graph class
    """

    def __init__(self, options):
        self._gnuplot = options.get_gnuplot()
        self._file = options.get_file()
        self._mode = options.get_mode()
        self._xcol = options.get_xcol()
        self._xrange = options.get_xrange()

        self._config_labels()
        self._graph()

    def _config_labels(self):
        if not os.path.isfile(self._file):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + self._file + '" data file.')
        try:
            with open(self._file, errors='replace') as ifile:
                line = ifile.readline().strip()
                if line[0] == '#':
                    self._labels = line[1:].split()
                else:
                    self._labels = []
                    for i in range(1, len(line.split()) + 1):
                        self._labels.append(str(i))
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + self._file + '" data file.')
        if len(self._labels) < 2:
            raise SystemExit(
                sys.argv[0] + ': Cannot find enough columns in "' + self._file + '" data file.')

    def _graph(self):
        if self._xcol > len(self._labels):
            raise SystemExit(
                sys.argv[0] + ': Cannot find column number "' + str(self._xcol) + '" in data file.')
        xlabel = self._labels[self._xcol - 1]
        for column in range(0, len(self._labels)):
            if column != self._xcol - 1:
                ylabel = self._labels[column]
                output = self._file + '_' + self._labels[column] + '.png'
                stdin = ('set terminal png', 'set output "' + output + '"',
                         'set xlabel "' + xlabel + '"', 'set ylabel "' + ylabel + '"',
                         'set title "' + self._file + ' vs ' + xlabel + '"',
                         'lot ' + self._xrange + '"' + self._file + '" u ' + str(self._xcol) +
                         ':' + str(column + 1) + ' t "' + ylabel + '" w ' + self._mode)
                self._writefile(self._file + '_' + self._labels[column] + '.plt', stdin)
                print('Plotting "' + output + '"...')
                self._gnuplot.run(stdin=stdin)
                if self._gnuplot.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' + str(self._gnuplot.get_exitcode()) +
                        ' received from "' + self._gnuplot.get_file() + '".')

    def _writefile(self, file, lines):
        try:
            with open(file, 'w', newline='\n') as ofile:
                for line in lines:
                    print(line, file=ofile)
        except OSError:
            return 1
        return 0


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
            Graph(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
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
