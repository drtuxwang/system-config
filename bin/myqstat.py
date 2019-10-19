#!/usr/bin/env python3
"""
MyQS, My Queuing System batch job statistics.
"""

import argparse
import glob
import os
import signal
import socket
import sys
import time

import task_mod

RELEASE = '2.7.10'


class Options:
    """
    Options class
    """
    def __init__(self):
        self._release = RELEASE
        self._args = None
        self.parse(sys.argv)

    def get_release(self):
        """
        Return release version.
        """
        return self._release

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='MyQS v' + self._release +
            ', My Queuing System batch job submission.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

    def _myqsd(self):
        lockfile = os.path.join(self._myqsdir, 'myqsd.pid')
        try:
            with open(lockfile, errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if task_mod.Tasks.factory().haspid(pid):
                        return
                    os.remove(lockfile)
        except OSError:
            pass
        print('MyQS batch job scheduler not running. Run "myqsd" command.')

    def _showjobs(self):
        print(
            'JOBID  QUEUENAME  JOBNAME                                     '
            'CPUS  STATE  TIME'
        )
        jobids = []
        for file in glob.glob(os.path.join(self._myqsdir, '*.[qr]')):
            try:
                jobids.append(int(os.path.basename(file)[:-2]))
            except ValueError:
                pass
        for jobid in sorted(jobids):
            try:
                ifile = open(
                    os.path.join(self._myqsdir, str(jobid) + '.q'),
                    errors='replace'
                )
            except OSError:
                try:
                    ifile = open(
                        os.path.join(self._myqsdir, str(jobid) + '.r'),
                        errors='replace'
                    )
                except OSError:
                    continue
                state = 'RUN'
            else:
                state = 'QUEUE'
            info = {}
            for line in ifile:
                line = line.strip()
                if '=' in line:
                    info[line.strip().split('=')[0]] = line.split('=', 1)[1]
            ifile.close()
            if 'NCPUS' in info:
                self._show_details(info, jobid, state)
        print()

    @staticmethod
    def _show_details(info, jobid, state):
        output = []
        if 'START' in info:
            try:
                etime = str(int((time.time() - float(info['START'])) / 60.))
                pgid = int(info['PGID'])
            except ValueError:
                etime = '0'
            else:
                if task_mod.Tasks.factory().haspgid(pgid):
                    if os.path.isdir(info['DIRECTORY']):
                        logfile = os.path.join(
                            info['DIRECTORY'],
                            os.path.basename(info['COMMAND']) +
                            '.o' + str(jobid)
                        )
                    else:
                        logfile = os.path.join(
                            os.environ['HOME'],
                            os.path.basename(info['COMMAND']) +
                            '.o' + str(jobid)
                        )
                    try:
                        with open(logfile, errors='replace') as ifile:
                            output = []
                            for line in ifile:
                                output = (output + [line.rstrip()])[-5:]
                    except OSError:
                        pass
                else:
                    state = 'STOP'
        else:
            etime = '-'
        print("{0:5d}  {1:9s}  {2:42s}  {3:>3s}   {4:5s} {5:>5s}".format(
            jobid,
            info['QUEUE'],
            info['COMMAND'],
            info['NCPUS'],
            state,
            etime
        ))
        for line in output:
            print(line)

    def run(self):
        """
        Start program
        """
        options = Options()

        host = socket.gethostname().split('.')[0].lower()
        print(
            '\nMyQS', options.get_release(),
            ', My Queuing System batch job statistics on HOST "' +
            host + '".\n'
        )
        if 'HOME' not in os.environ:
            raise SystemExit(
                sys.argv[0] + ': Cannot determine home directory.')
        self._myqsdir = os.path.join(
            os.environ['HOME'], '.config', 'myqs', host)
        self._showjobs()
        self._myqsd()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
