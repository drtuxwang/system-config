#!/usr/bin/env python3
"""
Generate multiple graph files with X/Y plots.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List, Sequence

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_file(self) -> str:
        """
        Return file.
        """
        return self._args.file[0]

    def get_gnuplot(self) -> command_mod.Command:
        """
        Return gnuplot Command class object.
        """
        return self._gnuplot

    def get_mode(self) -> str:
        """
        Return operation mode.
        """
        return self._args.mode

    def get_xcol(self) -> int:
        """
        Return X column.
        """
        return self._args.xcol[0]

    def get_xrange(self) -> str:
        """
        Return X range.
        """
        return self._xrange

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Generate multiple graph files with X/Y plots.',
        )

        parser.add_argument(
            '-mode',
            nargs=1,
            choices=['l', 'p', 'lp'],
            default='lp',
            help='Select lines(l), points(p) or both (lp). Default is lp.'
        )
        parser.add_argument(
            '-xcol',
            nargs=1,
            type=int,
            default=[1],
            help='Select column number for X-axis.'
        )
        parser.add_argument(
            '-xrange',
            nargs=1,
            metavar='n:n',
            help='Select range for X-axis.'
        )
        parser.add_argument(
            'file',
            nargs=1,
            help='Text file containing data.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._gnuplot = command_mod.Command('gnuplot', errors='stop')

        if self._args.xcol[0] < 1:
            raise SystemExit(
                sys.argv[0] + ': You must specific a positive integer for '
                'X-axis column number.'
            )

        if self._args.xrange:
            self._xrange = '[' + self._args.xrange[0] + '] '
        else:
            self._xrange = ''


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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
    def _config_labels(file: str) -> List[str]:
        if not os.path.isfile(file):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + file + '" data file.')
        try:
            with open(file, errors='replace') as ifile:
                line = ifile.readline().strip()
                if line[0] == '#':
                    labels = line[1:].split()
                else:
                    labels = []
                    for i in range(1, len(line.split()) + 1):
                        labels.append(str(i))
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" data file.'
            ) from exception
        if len(labels) < 2:
            raise SystemExit(
                sys.argv[0] + ': Cannot find enough columns in "' +
                file + '" data file.'
            )
        return labels

    def _graph(self) -> None:
        if self._xcol > len(self._labels):
            raise SystemExit(
                sys.argv[0] + ': Cannot find column number "' +
                str(self._xcol) + '" in data file.'
            )
        xlabel = self._labels[self._xcol - 1]
        for column, label in enumerate(self._labels):
            if column != self._xcol - 1:
                ylabel = label
                output = self._file + '_' + label + '.png'
                stdin = (
                    'set terminal png',
                    'set output "' + output + '"',
                    'set xlabel "' + xlabel + '"',
                    'set ylabel "' + ylabel + '"',
                    'set title "' + self._file + ' vs ' + xlabel + '"',
                    'lot ' + self._xrange + '"' + self._file +
                    '" u ' + str(self._xcol) + ':' + str(column + 1) +
                    ' t "' + ylabel + '" w ' + self._mode
                )
                self._writefile(self._file + '_' + label + '.plt', stdin)
                print('Plotting "' + output + '"...')
                task = subtask_mod.Task(self._gnuplot.get_cmdline())
                task.run(stdin=stdin)
                if task.get_exitcode():
                    raise SystemExit(
                        sys.argv[0] + ': Error code ' +
                        str(task.get_exitcode()) + ' received from "' +
                        task.get_file() + '".'
                    )

    @staticmethod
    def _writefile(file: str, lines: Sequence[str]) -> int:
        try:
            with open(file, 'w', newline='\n') as ofile:
                for line in lines:
                    print(line, file=ofile)
        except OSError:
            return 1
        return 0

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._gnuplot = options.get_gnuplot()
        self._file = options.get_file()
        self._mode = options.get_mode()
        self._xcol = options.get_xcol()
        self._xrange = options.get_xrange()

        self._labels = self._config_labels(self._file)
        self._graph()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
