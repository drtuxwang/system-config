#!/usr/bin/env python3
"""
Wrapper for 'nautilus' command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        self._nautilus = syslib.Command('nautilus')
        if len(args) == 1:
            if 'DESKTOP_STARTUP_ID' not in os.environ:
                self._nautilus.setArgs([os.getcwd()])
        else:
            self._nautilus.setArgs(args[1:])
        self._filter = ('^$|^Initializing nautilus|: Gtk-WARNING |: Gtk-CRITICAL | '
                        'GLib.*CRITICAL |^Shutting down')
        self._config()

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getNautilus(self):
        """
        Return nautilus Command class object.
        """
        return self._nautilus

    def _config(self):
        if 'HOME' in os.environ:
            self._configdir = os.path.join(os.environ['HOME'], '.local', 'share', 'applications')
            if not os.path.isdir(self._configdir):
                try:
                    os.makedirs(self._configdir)
                except OSError:
                    return
            file = os.path.join(self._configdir, 'mimeapps.list')
            if not os.path.isfile(file):
                try:
                    with open(file, 'w', newline='\n') as ofile:
                        print('[Added Associations]', file=ofile)
                        print('audio/ac3=vlc.desktop;', file=ofile)
                        print('audio/mp4=vlc.desktop;', file=ofile)
                        print('audio/mpeg=vlc.desktop;', file=ofile)
                        print('audio/vnd.rn-realaudio=vlc.desktop;', file=ofile)
                        print('audio/vorbis=vlc.desktop;', file=ofile)
                        print('audio/x-adpcm=vlc.desktop;', file=ofile)
                        print('audio/x-matroska=vlc.desktop;', file=ofile)
                        print('audio/x-mpegurl=vlc.desktop;', file=ofile)
                        print('audio/x-mp2=vlc.desktop;', file=ofile)
                        print('audio/x-mp3=vlc.desktop;', file=ofile)
                        print('audio/x-ms-wma=vlc.desktop;', file=ofile)
                        print('audio/x-scpls=vlc.desktop;', file=ofile)
                        print('audio/x-vorbis=vlc.desktop;', file=ofile)
                        print('audio/x-wav=vlc.desktop;', file=ofile)
                        print('image/jpeg=gqview.desktop;', file=ofile)
                        print('video/avi=vlc.desktop;', file=ofile)
                        print('video/mp4=vlc.desktop;', file=ofile)
                        print('video/mpeg=vlc.desktop;', file=ofile)
                        print('video/quicktime=vlc.desktop;', file=ofile)
                        print('video/vnd.rn-realvideo=vlc.desktop;', file=ofile)
                        print('video/x-matroska=vlc.desktop;', file=ofile)
                        print('video/x-ms-asf=vlc.desktop;', file=ofile)
                        print('video/x-msvideo=vlc.desktop;', file=ofile)
                        print('video/x-ms-wmv=vlc.desktop;', file=ofile)
                        print('video/x-ogm=vlc.desktop;', file=ofile)
                        print('video/x-theora=vlc.desktop;', file=ofile)
                        print('\n# xdg-open (ie "xdg-mime default vlc.desktop '
                              'x-scheme-handler/rtsp"', file=ofile)
                        print('[Default Applications]', file=ofile)
                        print('x-scheme-handler/mms=vlc.desktop', file=ofile)
                        print('x-scheme-handler/mms=vlc.desktop', file=ofile)
                        print('x-scheme-handler/rtsp=vlc.desktop', file=ofile)
                except IOError:
                    return
            self._userapp('application/vnd.oasis.opendocument.text', 'soffice')
            self._userapp('image/jpeg', 'gqview')
            self._userapp('text/html', 'chrome')

    def _userapp(self, mimeType, appName):
        file = os.path.join(self._configdir, appName + '-userapp.desktop')
        if not os.path.isfile(file):
            try:
                with open(file, 'w', newline='\n') as ofile:
                    print('[Desktop Entry]', file=ofile)
                    print('Name=' + appName, file=ofile)
                    print('Exec=' + appName, ' %f', file=ofile)
                    print('Type=Application', file=ofile)
                    print('NoDisplay=true', file=ofile)
            except IOError:
                return

        file = os.path.join(self._configdir, 'mimeinfo.cache')
        try:
            if not os.path.isfile(file):
                with open(file, 'w', newline='\n') as ofile:
                    print('[MIME Cache]', file=ofile)
            with open(file, errors='replace') as ifile:
                if mimeType + '=' + appName + '-userapp.desktop' in ifile:
                    return
            with open(file, 'a', newline='\n') as ofile:
                print(mimeType + '=' + appName + '-userapp.desktop', file=ofile)
        except IOError:
            return


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getNautilus().run(filter=options.getFilter(), mode='background')
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
