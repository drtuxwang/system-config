#!/usr/bin/env python3
"""
Run command on a subnet in parallel.
"""

import argparse
import glob
import os
import re
import signal
import sys
import threading
import time

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._ssh = syslib.Command('ssh')
        self._ssh.setFlags(['-o', 'StrictHostKeyChecking=no', '-o',
                            'UserKnownHostsFile=/dev/null', '-o', 'BatchMode=yes'])

    def getCommandLine(self):
        """
        Return command line.
        """
        return self._args.command + self._commandArgs

    def getSsh(self):
        """
        Return ssh Command class object.
        """
        return self._ssh

    def getSubnet(self):
        """
        Return subnet.
        """
        return self._subnet

    def _getmyip(self):
        myip = ''
        if syslib.info.getSystem() == 'linux':
            os.environ['LANG'] = 'en_GB'
            ifconfig = syslib.Command(file='/sbin/ifconfig', args=['-a'])
            ifconfig.run(filter=' inet addr[a-z]*:', mode='batch')
            for line in ifconfig.getOutput():
                myip = line.split(':')[1].split()[0]
                if myip not in ('', '127.0.0.1'):
                    break
        elif syslib.info.getSystem() == 'sunos':
            ifconfig = syslib.Command(file='/sbin/ifconfig', args=['-a'])
            ifconfig.run(filter='\tinet [^ ]+ netmask', mode='batch')
            for line in ifconfig.getOutput():
                myip = line.split()[1]
                if myip not in ('', '127.0.0.1'):
                    break
        return myip

    def _parseArgs(self, args):
        issubnet = re.compile('^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]0$')

        parser = argparse.ArgumentParser(description='Run command on a subnet in parallel.\n')

        parser.add_argument('-subnet', nargs=1, metavar='netmask',
                            help='Select netmask in the format "192.168.149.0".')

        parser.add_argument('command', nargs=1, help='Command to run on all systems.')
        parser.add_argument('args', nargs='*', metavar='arg', help='Command argument.')

        myArgs = []
        while len(args):
            myArgs.append(args[0])
            if not args[0].startswith('-'):
                break
            elif args[0] == '-subnet' and len(args) >= 2:
                args = args[1:]
                myArgs.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(myArgs)

        self._commandArgs = args[1:]

        if self._args.subnet and issubnet.match(self._args.subnet[0]):
            self._subnet = self._args.subnet[0]
        else:
            myip = self._getmyip()
            if not myip:
                raise SystemExit(sys.argv[0] + ": Cannot determine subnet configuration.")
            self._subnet = myip.rsplit('.', 1)[0]


class Remote(threading.Thread):

    def __init__(self, options, ip):
        self._options = options
        threading.Thread.__init__(self)
        self._ip = ip
        self._output = ''

    def getOutput(self):
        return self._output

    def run(self):
        ssh = self._options.getSsh()
        ssh.setArgs([self._ip] + ['echo "=== ' + self._ip + ': "`uname -s -n`" ==="; ' +
                    ssh.args2cmd(self._options.getCommandLine())])
        self._child = ssh.run(mode='child', error2output=True)
        self._child.stdin.close()
        while True:
            byte = self._child.stdout.read(1)
            if not byte:
                break
            self._output += byte.decode('utf-8', 'replace')

    def kill(self):
        if self._child:
            self._child.kill()
            self._child = None


class Cluster:

    def __init__(self, options):
        self._waitMax = 64
        self._waitTime = 0.1

        self._options = options
        self._threads = []
        self._bcast()
        self._allreduce()
        self._output()

    def _allreduce(self):
        print('\rAllreduce from subnet "' + self._options.getSubnet() + '.0"...')
        obytes = 0
        same = 0
        alive = True

        while alive:
            bytes = 0
            alive = False
            for thread in self._threads:
                bytes += len(thread.getOutput())
                if thread.is_alive():
                    alive = True
            sys.stdout.write('\r  -> Received ' + str(bytes) + ' bytes...')
            sys.stdout.flush()
            if bytes == obytes:
                same += 1
                if same > self._waitMax:
                    break
            else:
                same = 0
                obytes = bytes
            time.sleep(self._waitTime)
        print()

    def _bcast(self):
        print('Bcast to subnet "' + self._options.getSubnet() + '.0"...')
        for host in range(1, 255):
            ip = self._options.getSubnet() + '.' + str(host)
            sys.stdout.write('\r  -> ' + str(ip) + '...')
            sys.stdout.flush()
            thread = Remote(self._options, ip)
            thread.start()
            self._threads.append(thread)

    def _output(self):
        iserror = re.compile('Command not supported|Network is unreachable|No route to host|'
                             'Permission denied.|protocol failure in circuit setup', re.IGNORECASE)

        for thread in self._threads:
            output = thread.getOutput()
            if output and not iserror.search(output):
                print(thread.getOutput().rstrip('\r\n'))

        for thread in self._threads:
            thread.kill()


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Cluster(options)
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
