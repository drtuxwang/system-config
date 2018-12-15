#!/usr/bin/env python3
"""
Wrapper for "wget" command
"""

import glob
import os
import shutil
import signal
import sys

import command_mod
import network_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
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
        self._wget = command_mod.Command('wget', errors='stop')
        if '--no-check-certificate' not in args:
            self._wget.append_arg('--no-check-certificate')
        if '--timestamping' not in args:
            self._wget.append_arg('--timestamping')

        # Replace '-O' with '--output-document'
        args = ['--output-document' if x == '-O' else x for x in args]

        # Add '--output-document' for Firefox
        if '--output-document' not in args:
            for arg in args:
                if arg.startswith('--user-agent=') and 'Firefox/' in arg:
                    self._wget.extend_args(
                        ['--output-document', os.path.basename(args[-1])])
                    break

        self._output = ''
        while len(args) > 1:
            if (len(args) > 2 and args[1] in ('--output-document', '-O') and
                    not args[2].endswith('.part')):
                self._output = args[2]
                if (
                        os.path.isfile(args[2]) or
                        os.path.isfile(args[2] + '.part')
                ):
                    self._output = ('-'+str(os.getpid())+'.').join(
                        self._output.rsplit('.', 1))
                self._wget.extend_args([args[1], self._output + '.part'])
                args = args[2:]
                continue
            self._wget.append_arg(args[1])
            args = args[1:]


class Main:
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

        shaper = network_mod.Shaper()
        if shaper.is_found():
            cmdline = shaper.get_cmdline() + wget.get_cmdline()
        else:
            cmdline = wget.get_cmdline()

        if output:
            task = subtask_mod.Task(cmdline)
            task.run()
            if task.get_exitcode():
                raise SystemExit(task.get_exitcode())
            try:
                shutil.move(output + '.part', output)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + output +
                    '" output file.'
                )
        else:
            subtask_mod.Exec(cmdline).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
