#!/usr/bin/env python3
"""
Wrapper for 'smplayer' command
"""

import glob
import os
import signal
import sys
import time

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._smplayer = syslib.Command('smplayer')
        if len(args) > 1:
            if args[1].endswith('.ram'):
                self._smplayer.set_flags(['-playlist'])  # Avoid 'avisynth.dll' error

        self._smplayer.set_args(args[1:])

        self._filter = ('^Debug: |^Failed to load module: |^Preferences::load|^Warning: |'
                        '^global_init|^main: |: wrong ELF class:|^This is SMPlayer')

        if 'HOME' in os.environ:
            self._config()
            self._config2()

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_smplayer(self):
        """
        Return smplayer Command class object.
        """
        return self._smplayer

    def _config(self):
        configdir = os.path.join(os.environ['HOME'], '.config', 'smplayer')
        if not os.path.isdir(configdir):
            try:
                os.makedirs(configdir)
            except OSError:
                return
        os.chmod(configdir, int('700', 8))
        lines = []
        try:
            with open(os.path.join(configdir, 'smplayer.ini'), errors='replace') as ifile:
                for line in ifile:
                    lines.append(line.rstrip('\r\n'))
        except IOError:
            pass

        if 'use_single_instance=false' not in lines or 'cache_for_streams=100' not in lines:
            try:
                with open(os.path.join(configdir, 'smplayer.ini'), 'w', newline='\n') as ofile:
                    print('[defaults]', file=ofile)
                    print('initial_volume=200', file=ofile)
                    print('initial_volnorm=true', file=ofile)
                    print('[instances]', file=ofile)
                    print('use_single_instance=false', file=ofile)
                    print('[%General]', file=ofile)
                    print('use_double_buffer=false', file=ofile)
                    print('[history]', file=ofile)
                    print(r'recents\max_items=0', file=ofile)
                    print('[performance]', file=ofile)
                    print('hard_frame_drop=true', file=ofile)
                    print('cache_for_streams=100', file=ofile)
                    print('[mplayer_info]', file=ofile)
                    print('mplayer_user_supplied_version=20372', file=ofile)
            except IOError:
                return

        configfile = os.path.join(os.environ['HOME'], '.config', 'smplayer', 'smplayer.ini')
        try:
            with open(configfile, errors='replace') as ifile:
                lines = []
                for line in ifile:
                    lines.append(line.rstrip('\r\n'))
        except IOError:
            try:
                with open(configfile, 'w', newline='\n') as ofile:
                    print('[gui]', file=ofile)
                    print('reported_mplayer_is_old=true\n', file=ofile)
                    print('[instances]', file=ofile)
                    print('use_single_instance=false\n', file=ofile)
            except IOError:
                return

        try:
            with open(configfile + '-new', 'w', newline='\n') as ofile:
                for line in lines:
                    if line == 'compact_mode=true':
                        # Fix missing titlebar
                        print('compact_mode=false', file=ofile)
                    elif line == 'use_single_instance=true':
                        print('use_single_instance=false', file=ofile)
                    elif line == 'osd=2':
                        # Fix missing titlebar
                        print('osd=1', file=ofile)
                    elif line.startswith('toolbars_state='):
                        pass
                    else:
                        print(line, file=ofile)
                try:
                    os.rename(configfile + '-new', configfile)
                except OSError:
                    os.remove(configfile + '-new')
        except IOError:
            pass

    def _config2(self):
        configdir = os.path.join(os.environ['HOME'], '.config', 'smplayer')
        expiry = 2592000  # 30 days
        mytime = time.time()

        for directory in glob.glob(os.path.join(configdir, 'file_settings', '*')):
            empty = True
            for file in glob.glob(os.path.join(directory, '*')):
                if mytime - syslib.FileStat(file).get_time() < expiry:
                    try:
                        with open(file, errors='replace') as ifile:
                            ifile.readline()
                            if ifile.readline().rstrip('\r\n') != 'current_sec=0':
                                empty = False
                                continue
                    except IOError:
                        pass
                self._remove(file)
            if empty:
                try:
                    os.rmdir(directory)
                except OSError:
                    pass

    def _remove(self, *files):
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass


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
            options.get_smplayer().run(filter=options.get_filter(), mode='background')
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
