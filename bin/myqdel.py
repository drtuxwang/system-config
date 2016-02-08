#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job deletion.
"""

import argparse
import glob
import os
import signal
import sys

import syslib
import task_mod

RELEASE = '2.7.3'

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._release = RELEASE
        self._args = None
        self.parse(sys.argv)

    def get_force_flag(self):
        """
        Return force flag.
        """
        return self._args.forceFlag

    def get_jobids(self):
        """
        Return list of job IDs.
        """
        return self._jobids

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release + ', My Queuing System batch job deletion.')

        parser.add_argument('-k', action='store_true', dest='forceFlag',
                            help='Force termination of running jobs.')

        parser.add_argument('jobIds', nargs='+', metavar='jobid',
                            help='Batch job ID.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._jobids = []
        for jobid in self._args.jobIds:
            if not jobid.isdigit():
                raise SystemExit(sys.argv[0] + ': Invalid "' + jobid + '" job ID.')
            self._jobids.append(jobid)


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

    def _remove(self, jobid):
        file = os.path.join(self._myqsdir, jobid + '.q')
        if os.path.isfile(file):
            try:
                os.remove(file)
            except OSError:
                pass
            else:
                print('Batch job with jobid', jobid, 'has been deleted from MyQS.')
                return
        file = os.path.join(self._myqsdir, jobid + '.r')
        if os.path.isfile(file):
            try:
                with open(file, errors='replace') as ifile:
                    if not self._force_flag():
                        print('MyQS cannot delete batch job with jobid', jobid, 'as it is running.')
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
                                return
                            task_mod.Task.factory().killpgid(pgid, signal='TERM')
                        try:
                            os.remove(file)
                        except OSError:
                            pass
                        print('Batch job with jobid', jobid, 'has been deleted from MyQS.')
            except OSError:
                pass

    def run(self):
        """
        Start program
        """
        options = Options()

        self._force_flag = options.get_force_flag()

        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')
        self._myqsdir = os.path.join(os.environ['HOME'], '.config',
                                     'myqs', syslib.info.get_hostname())
        for jobid in options.get_jobids():
            if not glob.glob(os.path.join(self._myqsdir, jobid + '.[qr]')):
                print('MyQS cannot delete batch job with jobid', jobid, 'as it does no exist.')
            else:
                self._remove(jobid)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
