#!/usr/bin/env python3
"""
VirtualBox virtual machine manager.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getMode(self):
        """
        Return operation mode.
        """
        return self._args.mode

    def getMachines(self):
        """
        Return list of virtual machines.
        """
        return self._args.machines

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='VirtualBox virtual machine manager.')

        parser.add_argument('-p', action='store_const', const='poweroff', dest='mode',
                            default='start', help='Power off virtual machine.')
        parser.add_argument('-s', action='store_const', const='shutdown', dest='mode',
                            default='start', help='Shutdown virtual machine.')
        parser.add_argument('-v', action='store_const', const='view', dest='mode',
                            default='start', help='List virtual machine.')

        parser.add_argument('machines', nargs='+', metavar='machine',
                            help='Virtual machine.')

        self._args = parser.parse_args(args)


class VBoxManage:

    def __init__(self, options):
        self._vboxmanage = syslib.Command('VBoxManage')
        mode = options.getMode()
        machines = options.getMachines()

        if mode == 'view':
            self._view()
        elif mode == 'poweroff':
            self._poweroff(machines)
        elif mode == 'shutdown':
            self._shutdown(machines)
        else:
            self._start(machines)

    def _poweroff(self, machines):
        for machine in machines:
            self._vboxmanage.setArgs(['controlvm', machine, 'poweroff'])
            self._vboxmanage.run()
            if self._vboxmanage.getExitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(self._vboxmanage.getExitcode()) +
                    ' received from "' + self._vboxmanage.getFile() + '".')

    def _shutdown(self, machines):
        for machine in machines:
            self._vboxmanage.setArgs(['controlvm', machine, 'acpipowerbutton'])
            self._vboxmanage.run()
            if self._vboxmanage.getExitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(self._vboxmanage.getExitcode()) +
                    ' received from "' + self._vboxmanage.getFile() + '".')

    def _start(self, machines):
        for machine in machines:
            self._vboxmanage.setArgs(['startvm', machine, '--type', 'headless'])
            self._vboxmanage.run()
            if self._vboxmanage.getExitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(self._vboxmanage.getExitcode()) +
                    ' received from "' + self._vboxmanage.getFile() + '".')

    def _view(self):
        self._vboxmanage.setArgs(['list', 'vms'])
        self._vboxmanage.run(filter='^".*"', mode='batch')
        if self._vboxmanage.hasOutput():
            lines = sorted(self._vboxmanage.getOutput())
            self._vboxmanage.setArgs(['list', 'runningvms'])
            self._vboxmanage.run(filter='^".*"', mode='batch')
            for line in lines:
                if line in self._vboxmanage.getOutput():
                    print('[Run]', line)
                else:
                    print('[Off]', line)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            VBoxManage(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
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


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
