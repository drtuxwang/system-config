#!/usr/bin/env python3
"""
JAVA jar tool launcher
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._jar = syslib.Command(os.path.join('bin', 'jar'))

        if len(args) == 1:
            self._jar.run(mode='exec')
        elif args[1][-4:] != '.jar':
            self._jar.set_args(args[1:])
            self._jar.run(mode='exec')

        self._jar_file = args[1]
        self._manifest = args[1][:-4]+'.manifest'
        self._files = args[2:]
        self._jar.set_flags(['cfvm', args[1], self._manifest])

    def get_files(self):
        """
        Return list of files.
        """
        return self._files

    def get_jar(self):
        """
        Return jar Command class object.
        """
        return self._jar

    def get_jar_file(self):
        """
        Return jar file location.
        """
        return self._jar_file

    def get_manifest(self):
        """
        Return manifest file location.
        """
        return self._manifest


class Pack(object):
    """
    Pack class
    """

    def __init__(self, options):
        self._jar = options.get_jar()
        self._jar_file = options.get_jar_file()
        self._manifest = options.get_manifest()

        for file in options.get_files():
            if file.endswith('.java'):
                self._compile(file)
                self._jar.append_arg(file[:-5]+'.class')
            else:
                self._jar.append_arg(file)
        self._create_manifest(options)
        print('Building "' + self._jar_file + '" Java archive file.')
        self._jar.run(mode='exec')

    def _compile(self, source):
        target = source[:-5]+'.class'
        if not os.path.isfile(source):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + source + '" Java source file.')
        if os.path.isfile(target):
            if syslib.FileStat(source).get_time() > syslib.FileStat(target).get_time():
                try:
                    os.remove(target)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot remove "' + target + '" Java class file.')
        if not os.path.isfile(target):
            javac = syslib.Command('javac', args=[source])
            print('Building "' + target + '" Java class file.')
            javac.run(mode='batch', error2output=True)
            if javac.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(javac.get_exitcode()) +
                                 ' received from "' + javac.get_file() + '".')
            for line in javac.get_output():
                print('  ' + line)
            if not os.path.isfile(target):
                raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" Java class file.')

    def _create_manifest(self, options):
        if not os.path.isfile(self._manifest):
            if 'Main.class' in self._jar.get_args():
                main = 'Main'
            else:
                main = self._jar_file[:-4]
            print('Building "' + self._manifest + '" Java manifest file with "' +
                  main + '" main class.')
            try:
                with open(self._manifest, 'w', newline='\n') as ofile:
                    print('Main-Class:', main, file=ofile)
            except IOError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + self._manifest + '" Java manifest file.')


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
            Pack(options)
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
