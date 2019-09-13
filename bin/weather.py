#!/usr/bin/env python3
"""
Current weather search (using accuweather)

London: http://www.accuweather.com/en/gb/london/ec4a-2/weather-forecast/328328
"""

import argparse
import json
import os
import signal
import sys
import time

import command_mod
import config_mod
import subtask_mod

if sys.version_info < (3, 4) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.4, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self._config()
        self.parse(sys.argv)

    def get_quiet_flag(self):
        """
        Return quiet flag.
        """
        return self._args.quiet_flag

    def get_url(self):
        """
        Return url.
        """
        return self._args.url[0]

    @staticmethod
    def _config():
        if 'REQUESTS_CA_BUNDLE' not in os.environ:
            for file in (
                    # Debian/Ubuntu
                    '/etc/ssl/certs/ca-certificates.crt',
                    # RHEL/CentOS
                    '/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt'
            ):
                if os.path.isfile(file):
                    os.environ['REQUESTS_CA_BUNDLE'] = file
                    break

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Current weather search.')

        parser.add_argument(
            '-q',
            action='store_true',
            dest='quiet_flag',
            help='Disable error messages'
        )
        parser.add_argument(
            'url',
            nargs=1,
            help='Weather data URL.'
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

    @staticmethod
    def _parse(text):
        try:
            data = json.loads(text.split('var curCon = ')[-1].split(';')[0])
        except json.decoder.JSONDecodeError:
            pass
        else:
            temp = data.get('temp', '')
            condition = data.get('phrase', '')
            if temp and condition:
                return '{0:s}C ({1:s})'.format(temp, condition)
        return None

    @classmethod
    def _search(cls, options):
        user_agent = config_mod.Config().get('user_agent')
        curl = command_mod.Command('curl', errors='stop')
        curl.set_args(['-A', user_agent, options.get_url()])
        task = subtask_mod.Batch(curl.get_cmdline())

        for _ in range(10):
            task.run()
            if task.get_exitcode():
                break
            weather = cls._parse('\n'.join(task.get_output()))
            if weather:
                return weather
            time.sleep(2)

        if options.get_quiet_flag():
            return ''
        return '???C (???)'

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()
        print(cls._search(options))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
