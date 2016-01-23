#!/usr/bin/env python3
"""
Make data/audio/video CD/DVD using CD/DVD writer.
"""

import argparse
import glob
import os
import signal
import sys
import time

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):

        self._parse_args(args[1:])

        if self._args.image != 'scan':
            self._device_detect()
        self._signal_trap()

    def get_device(self):
        """
        Return device location.
        """
        return self._device

    def get_erase_flag(self):
        """
        Return erase flag.
        """
        return self._args.eraseFlag

    def get_image(self):
        """
        Return ISO/BIN image file or audio directory.
        """
        return self._args.image[0]

    def get_md5_flag(self):
        """
        Return md5 flag.
        """
        return self._args.md5Flag

    def get_speed(self):
        """
        Return CD speed.
        """
        return self._args.speed[0]

    def _device_detect(self):
        if self._args.device:
            self._device = self._args.device[0]
        else:
            cdrom = Cdrom()
            if not cdrom.get_devices().keys():
                raise SystemExit(sys.argv[0] + ': Cannot find any CD/DVD device.')
            self._device = sorted(cdrom.get_devices().keys())[0]
        if not os.path.exists(self._device) and not os.path.isdir(self.get_image()):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + self._device + '" CD/DVD device.')

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Make data/audio/video CD/DVD using CD/DVD writer.')

        parser.add_argument('-dev', nargs=1, dest='device',
                            help='Select device (ie /dev/sr0).')
        parser.add_argument('-erase', dest='eraseFlag', action='store_true',
                            help='Erase TOC on CD-RW media before writing in DAO mode.')
        parser.add_argument('-md5', dest='md5Flag', action='store_true',
                            help='Verify MD5 check sum of data CD/DVD disk.')
        parser.add_argument('-speed', nargs=1, type=int, default=[8],
                            help='Select CD/DVD spin speed.')

        parser.add_argument('image', nargs=1, metavar='image.iso|image.bin|directory|scan',
                            help='ISO/BIn image file, audio or scan')

        self._args = parser.parse_args(args)

        if self._args.speed[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'CD/DVD device speed.')
        if self._args.image[0] != 'scan' and not os.path.isdir(self._args.image[0]):
            if not os.path.exists(self._args.image[0]):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + self._args.image[0] + '" CD/DVD device.')

    def _signal_ignore(self, signal, frame):
        pass

    def _signal_trap(self):
        signal.signal(signal.SIGINT, self._signal_ignore)
        signal.signal(signal.SIGTERM, self._signal_ignore)


class Burner(object):
    """
    CD/DVD burner class
    """

    def __init__(self, options):
        self._device = options.get_device()
        self._speed = options.get_speed()
        self._image = options.get_image()

        if self._image == 'scan':
            self._scan()
        elif os.path.isdir(self._image):
            self._track_at_once_audio()
        elif self._image.endswith('.bin'):
            self._disk_at_once_data(options)
        else:
            self._track_at_once_data(options)

    def _eject(self):
        eject = syslib.Command('eject', check=False)
        if eject.is_found():
            time.sleep(1)
            eject.run(mode='batch')
            if eject.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(eject.get_exitcode()) +
                                 ' received from "' + eject.get_file() + '".')

    def _scan(self):
        cdrom = Cdrom()
        print('Scanning for CD/DVD devices...')
        devices = cdrom.get_devices()
        for key, value in sorted(devices.items()):
            print('  {0:10s}  {1:s}'.format(key, value))

    def _disk_at_once_data(self, options):
        cdrdao = syslib.Command('cdrdao')
        if options.get_erase_flag():
            cdrdao.set_args(['blank', '--blank-mode', 'minimal', '--device', self._device,
                             '--speed', str(self._speed)])
            cdrdao.run()
            if cdrdao.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(cdrdao.get_exitcode()) +
                                 ' received from "' + cdrdao.get_file() + '".')
        cdrdao.set_flags(['write', '--device', self._device, '--speed', str(self._speed)])
        if os.path.isfile(self._files[0][:-4]+'.toc'):
            cdrdao.set_args([self._files[0][:-4]+'.toc'])
        else:
            cdrdao.set_args([self._files[0][:-4]+'.cue'])
        cdrdao.run()
        if cdrdao.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(cdrdao.get_exitcode()) +
                             ' received from "' + cdrdao.get_file() + '".')
        self._eject()

    def _track_at_once_audio(self):
        files = glob.glob(os.path.join(self._image[0], '*.wav'))

        wodim = syslib.Command('wodim')
        print('If your media is a rewrite-able CD/DVD its contents will be deleted.')
        answer = input('Do you really want to burn data to this CD/DVD disk? (y/n) [n] ')
        if answer.lower() != 'y':
            raise SystemExit(1)
        print('Using AUDIO mode for WAVE files (Audio tracks detected)...')
        wodim.set_args(['-v', '-shorttrack', '-audio', '-pad', '-copy', 'dev=' + self._device,
                        'speed=' + str(self._speed), 'driveropts=burnfree'] + files)
        wodim.run()
        if wodim.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(wodim.get_exitcode()) +
                             ' received from "' + wodim.get_file() + '".')

        time.sleep(1)
        icedax = syslib.Command('icedax', check=False)
        if icedax.is_found():
            icedax.set_args(['-info-only', '--no-infofile', 'verbose-level=toc',
                             'dev=' + self._device, 'speed=' + self._speed])
            icedax.run(mode='batch')
            toc = icedax.get_error(r'[.]\(.*:.*\)|^CD')
            if not toc:
                raise SystemExit(sys.argv[0] + ': Cannot find Audio CD media. Please check drive.')
            elif icedax.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(icedax.get_exitcode()) +
                                 ' received from "' + icedax.get_file() + '".')
            for line in toc:
                print(line)
        self._eject()

    def _track_at_once_data(self, options):
        file = options.get_image()

        wodim = syslib.Command('wodim')
        print('If your media is a rewrite-able CD/DVD its contents will be deleted.')
        answer = input('Do you really want to burn data to this CD/DVD disk? (y/n) [n] ')
        if answer.lower() != 'y':
            raise SystemExit(1)
        wodim.set_flags(['-v', '-shorttrack', '-eject'])
        if syslib.FileStat(file).get_size() < 2097152:  # Pad to avoid dd read problem
            wodim.append_arg('-pad')
        wodim.set_args([
            'dev=' + self._device, 'speed=' + str(self._speed), 'driveropts=burnfree', file])
        wodim.run()
        if wodim.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(wodim.get_exitcode()) +
                             ' received from "' + wodim.get_file() + '".')

        if options.get_md5_flag():
            print('Verifying MD5 check sum of data CD/DVD:')
            dd = syslib.Command('dd')
            dd.set_args(['if=' + self._device, 'bs=' + str(2048*360), 'count=1', 'of=/dev/null'])
            for _ in range(10):
                time.sleep(1)
                dd.run(mode='batch')
                if dd.has_output():
                    time.sleep(1)
                    break
            md5cd = syslib.Command('md5cd', args=[self._device])
            md5cd.run()
            if md5cd.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(md5cd.get_exitcode()) +
                                 ' received from "' + md5cd.get_file() + '".')
            try:
                with open(self._files[0][:-4] + '.md5', errors='replace') as ifile:
                    for line in ifile:
                        print(line.rstrip())
            except OSError:
                pass


class Cdrom(object):
    """
    CDROM class
    """

    def __init__(self):
        self._devices = {}
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

    def get_devices(self):
        """
        Return list of devices.
        """
        return self._devices


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
            Burner(options)
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
