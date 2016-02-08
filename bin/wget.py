#!/usr/bin/env python3
"""
Wrapper for 'wget' command
"""

import glob
import os
import signal
import sys

import netnice
import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_output(self):
        """
        Return output file.
        """
        return self._output

    def get_wget(self):
        """
        Return wget Command class object.
        """
        return self._wget

    def parse(self, args):
        """
        Parse arguments
        """
        self._wget = syslib.Command('wget')
        if '--no-check-certificate' in args:
            self._wget.append_flag('--no-check-certificate')
        if '--timestamping' in args:
            self._wget.append_flag('--timestamping')

        # Replace '-O' with '--output-document'
        args = ['--output-document' if x == '-O' else x for x in args]

        # Add '--output-document' for Firefox
        if '--output-document' not in args:
            for arg in args:
                if arg.startswith('--user-agent=') and 'Firefox/' in arg:
                    self._wget.extend_flags(['--output-document', os.path.basename(args[-1])])
                    break

        shaper = netnice.Shaper()
        if shaper.is_found():
            self._wget.set_wrapper(shaper)

        self._output = ''
        while len(args) > 1:
            if (len(args) > 2 and args[1] in ('--output-document', '-O') and
                    not args[2].endswith('.part')):
                self._output = args[2]
                if os.path.isfile(args[2]) or os.path.isfile(args[2] + '.part'):
                    self._output = ('-'+str(os.getpid())+'.').join(self._output.rsplit('.', 1))
                self._wget.extend_args([args[1], self._output + '.part'])
                args = args[2:]
                continue
            self._wget.append_arg(args[1])
            args = args[1:]


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

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()
        output = options.get_output()
        wget = options.get_wget()

        if output:
            wget.run()
            if wget.get_exitcode():
                raise SystemExit(wget.get_exitcode())
            try:
                os.rename(output + '.part', output)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + output + '" output file.')
        else:
            wget.run(mode='exec')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
