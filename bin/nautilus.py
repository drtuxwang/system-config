#!/usr/bin/env python3
"""
Wrapper for 'nautilus' command
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pattern(self):
        """
        Return filter pattern.
        """
        return self._pattern

    def get_nautilus(self):
        """
        Return nautilus Command class object.
        """
        return self._nautilus

    def _config(self):
        if 'HOME' in os.environ:
            configdir = os.path.join(os.environ['HOME'], '.local', 'share', 'applications')
            if not os.path.isdir(configdir):
                try:
                    os.makedirs(configdir)
                except OSError:
                    return
            file = os.path.join(configdir, 'mimeapps.list')
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
                except OSError:
                    return
            self._userapp(configdir, 'application/vnd.oasis.opendocument.text', 'soffice')
            self._userapp(configdir, 'image/jpeg', 'gqview')
            self._userapp(configdir, 'text/html', 'chrome')

    @staticmethod
    def _userapp(configdir, mime_type, app_name):
        file = os.path.join(configdir, app_name + '-userapp.desktop')
        if not os.path.isfile(file):
            try:
                with open(file, 'w', newline='\n') as ofile:
                    print('[Desktop Entry]', file=ofile)
                    print('Name=' + app_name, file=ofile)
                    print('Exec=' + app_name, ' %f', file=ofile)
                    print('Type=Application', file=ofile)
                    print('NoDisplay=true', file=ofile)
            except OSError:
                return

        file = os.path.join(configdir, 'mimeinfo.cache')
        try:
            if not os.path.isfile(file):
                with open(file, 'w', newline='\n') as ofile:
                    print('[MIME Cache]', file=ofile)
            with open(file, errors='replace') as ifile:
                if mime_type + '=' + app_name + '-userapp.desktop' in ifile:
                    return
            with open(file, 'a', newline='\n') as ofile:
                print(mime_type + '=' + app_name + '-userapp.desktop', file=ofile)
        except OSError:
            return

    def parse(self, args):
        """
        Parse arguments
        """
        self._nautilus = syslib.Command('nautilus')
        if len(args) == 1:
            if 'DESKTOP_STARTUP_ID' not in os.environ:
                self._nautilus.set_args([os.getcwd()])
        else:
            self._nautilus.set_args(args[1:])
        self._pattern = ('^$|^Initializing nautilus|: Gtk-WARNING |: Gtk-CRITICAL | '
                         'GLib.*CRITICAL |^Shutting down')
        self._config()


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
        except (syslib.SyslibError, SystemExit) as exception:
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

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        options.get_nautilus().run(filter=options.get_pattern(), mode='background')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
