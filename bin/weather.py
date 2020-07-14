#!/usr/bin/env python3
"""
Current weather search (using Accuweather website)

London: https://www.accuweather.com/en/gb/london/ec4a-2/weather-forecast/328328
"""

import argparse
import signal
import sys
import time

import command_mod
import config_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
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
            data = text.split('Current Weather')[1]
        except IndexError:
            return
        try:
            temp = data.split('<div class="temp">')[1].split('<')[0]
            condition = data.split('<span class="phrase">')[1].split('<')[0]
            if temp and condition:
                return '{0:s}C ({1:s})'.format(
                    temp.replace('&#xB0;', '°').strip(),
                    condition.strip(),
                )
        except IndexError:
            return '???'
        return None

    @classmethod
    def _search(cls, options):
        user_agent = config_mod.Config().get('user_agent')
        curl = command_mod.Command('curl', errors='stop')
        curl.set_args(['-A', user_agent, options.get_url()])
        task = subtask_mod.Batch(curl.get_cmdline())
        quiet = options.get_quiet_flag()

        if not quiet:
            print("Connecting...")
        for _ in range(10):
            task.run()
            if task.get_exitcode():
                break
            weather = cls._parse('\n'.join(task.get_output()))
            if weather:
                return weather
            time.sleep(2)
            if not quiet:
                print("Retrying...")

        if quiet:
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
