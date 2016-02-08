#!/usr/bin/env python3
"""
Rip CD audio tracks as WAVE sound files.
"""

import argparse
import glob
import os
import re
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_device(self):
        """
        Return device location.
        """
        return self._args.device[0]

    def get_icedax(self):
        """
        Return icedax Command class object.
        """
        return self._icedax

    def get_speed(self):
        """
        Return CD speed.
        """
        return self._args.speed[0]

    def get_tracks(self):
        """
        Return list of track numbers.
        """
        return self._tracks

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Rip CD audio tracks as WAVE sound files.')

        parser.add_argument('-speed', nargs=1, type=int, default=[8],
                            help='Select CD spin speed.')
        parser.add_argument('-tracks', nargs=1, metavar='n[,n...]',
                            help='Select CD tracks to rip.')
        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='View CD table of contents only.')

        parser.add_argument('device', nargs=1, metavar='device|scan',
                            help='CD/DVD device (ie "/dev/sr0" or "scan".')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._icedax = syslib.Command('icedax')

        if self._args.speed[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'CD/DVD device speed.')
        if self._args.device[0] != 'scan' and not os.path.exists(self._args.device[0]):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.device[0] + '" CD/DVD device.')

        if self._args.tracks:
            self._tracks = self._args.tracks.split(',')
        else:
            self._tracks = None


class Cdrom(object):
    """
    CDROM class
    """

    def __init__(self):
        self._devices = {}
        self.detect()

    def get_devices(self):
        """
        Return list of devices
        """
        return self._devices

    def detect(self):
        """
        Detect devices
        """
        for directory in glob.glob('/sys/block/sr*/device'):
            device = '/dev/' + os.path.basename(os.path.dirname(directory))
            model = ''
            for file in ('vendor', 'model'):
                try:
                    with open(os.path.join(directory, file), errors='replace') as ifile:
                        model += ' ' + ifile.readline().strip()
                except OSError:
                    continue
            self._devices[device] = model


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            self._toc = None
            self._tracks = None
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

    def _rip_tracks(self, ntracks):
        tee = syslib.Command('tee')

        for track in self._tracks:
            istrack = re.compile('^.* ' + track + r'[.]\( *')
            length = 'Unknown'
            for line in self._toc:
                if istrack.search(line):
                    minutes, seconds = istrack.sub('', line).split(')')[0].split(':')
                    try:
                        length = '{0:4.2f}'.format(int(minutes)*60 + float(seconds))
                    except ValueError:
                        pass
                    break
            logfile = track.zfill(2) + '.log'
            try:
                with open(logfile, 'w', newline='\n') as ofile:
                    line = ('\nRipping track ' + track + '/' + str(ntracks) +
                            ' (' + length + ' seconds)')
                    print(line)
                    print(line, file=ofile)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + logfile + '" file.')
            warnfile = track.zfill(2) + '.warning'
            try:
                with open(warnfile, 'wb'):
                    pass
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + warnfile + '" file.')
            wavfile = track.zfill(2) + '.wav'
            self._icedax.set_args(['verbose-level=disable', 'track=' + track, 'dev=' +
                                   self._device, wavfile, '2>&1'])
            tee.set_args(['-a', logfile])
            self._icedax.run(pipes=[tee])
            if self._icedax.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(self._icedax.get_exitcode()) +
                                 ' received from "' + self._icedax.get_file() + '".')
            if os.path.isfile(wavfile):
                self._pregap(wavfile)
            if not self._hasprob(logfile):
                os.remove(warnfile)

    def _rip(self):
        self._icedax.set_flags(['-vtrackid', '-paranoia', '-S=' + str(self._speed),
                                '-K', 'dsp', '-H'])
        try:
            with open('00.log', 'w', newline='\n') as ofile:
                for line in self._toc:
                    print(line, file=ofile)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "00.log" TOC file.')
        try:
            ntracks = int(self._toc[-1].split('.(')[-2].split()[-1])
        except (IndexError, ValueError):
            raise SystemExit(sys.argv[0] + ": Unable to detect the number of audio tracks.")
        if not self._tracks:
            self._tracks = [str(i) for i in range(1, int(ntracks) + 1)]

        self._rip_tracks(ntracks)

    @staticmethod
    def _hasprob(logfile):
        with open(logfile, errors='replace') as ifile:
            for line in ifile:
                line = line.rstrip('\r\n')
                if line.endswith('problems'):
                    if line[-14:] != 'minor problems':
                        ifile.close()
                        return True
        return False

    @staticmethod
    def _pregap(wavfile):
        size = syslib.FileStat(wavfile).get_size()
        with open(wavfile, 'rb+') as ifile:
            ifile.seek(size - 2097152)
            data = ifile.read(2097152)
            for i in range(len(data) - 1, 0, -1):
                if data[i] != 0:
                    newsize = size - len(data) + i + 264
                    if newsize < size:
                        line = 'Track length is ' + str(newsize) + ' bytes (pregap removed)'
                        print(line)
                        ifile.truncate(newsize)
                    break

    @staticmethod
    def _scan():
        cdrom = Cdrom()
        print('Scanning for CD/DVD devices...')
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print('  {0:10s}  {1:s}'.format(key, value))

    def _read_toc(self):
        self._icedax.set_args(['-info-only', '--no-infofile', 'verbose-level=toc',
                               'dev=' + self._device, 'speed=' + str(self._speed)])
        self._icedax.run(mode='batch')
        self._toc = self._icedax.get_error(r'[.]\(.*:.*\)')
        if not self._toc:
            raise SystemExit(sys.argv[0] + ': Cannot find Audio CD media. Please check drive.')
        if self._icedax.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._icedax.get_exitcode()) +
                             ' received from "' + self._icedax.get_file() + '".')
        for line in self._icedax.get_error(r'[.]\(.*:.*\)|^CD'):
            print(line)

    def run(self):
        """
        Start program
        """
        options = Options()

        self._icedax = options.get_icedax()
        self._device = options.get_device()
        self._speed = options.get_speed()
        self._tracks = options.get_tracks()

        if self._device == 'scan':
            self._scan()
        else:
            self._read_toc()
            self._rip()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
