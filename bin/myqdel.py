#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job deletion.
"""

RELEASE = '2.6.3'

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._release = RELEASE

        self._parseArgs(args[1:])

    def getForceFlag(self):
        """
        Return force flag.
        """
        return self._args.forceFlag

    def getJobids(self):
        """
        Return list of job IDs.
        """
        return self._jobids

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release + ', My Queuing System batch job deletion.')

        parser.add_argument('-k', action='store_true', dest='forceFlag',
                            help='Force termination of running jobs.')

        parser.add_argument('jobIds', nargs='+', metavar='jobid',
                            help='Batch job ID.')

        self._args = parser.parse_args(args)

        self._jobids = []
        for jobid in self._args.jobIds:
            if not jobid.isdigit():
                raise SystemExit(sys.argv[0] + ': Invalid "' + jobid + '" job ID.')
            self._jobids.append(jobid)


class Delete(syslib.Dump):

    def __init__(self, options):
        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        self._myqsdir = os.path.join(os.environ['HOME'], '.config',
                                     'myqs', syslib.info.getHostname())
        for jobid in options.getJobids():
            if not glob.glob(os.path.join(self._myqsdir, jobid + '.[qr]')):
                print('MyQS cannot delete batch job with jobid', jobid, 'as it does no exist.')
            else:
                file = os.path.join(self._myqsdir, jobid + '.q')
                if os.path.isfile(file):
                    try:
                        os.remove(file)
                    except OSError:
                        pass
                    else:
                        print('Batch job with jobid', jobid, 'has been deleted from MyQS.')
                        continue
                file = os.path.join(self._myqsdir, jobid + '.r')
                if os.path.isfile(file):
                    try:
                        with open(file, errors='replace') as ifile:
                            if not options.getForceFlag():
                                print('MyQS cannot delete batch job with jobid', jobid,
                                      'as it is running.')
                            else:
                                info = {}
                                for line in ifile:
                                    line = line.strip()
                                    if '=' in line:
                                        info[line.split('=')[0]] = line.split('=', 1)[1]
                                if 'PGID' in info:
                                    try:
                                        pgid = int(info['PGID'])
                                    except ValueError:
                                        continue
                                    syslib.Task().killpgid(pgid, signal='TERM')
                                try:
                                    os.remove(file)
                                except OSError:
                                    pass
                                print('Batch job with jobid', jobid, 'has been deleted from MyQS.')
                    except IOError:
                        continue


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Delete(options)
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
