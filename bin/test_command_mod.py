#!/usr/bin/env python3
"""
Test module for 'command_mod.py' module
"""

import sys
import unittest

import command_mod


class TestLooseVersion(unittest.TestCase):
    """
    This class tests LooseVersion class.
    """

    def test_get_version(self) -> None:
        """
        Test getting version.
        """
        expected = '1.2.3-4'

        loose_version = command_mod.LooseVersion('1.2.3-4')

        result = loose_version.get_version()
        self.assertEqual(result, expected)

    def test_get_tokens_version(self) -> None:
        """
        Test getting version.
        """
        expected = ['• ', '1', '.', '2', '.', '3', '-', '4', ' •']

        loose_version = command_mod.LooseVersion('1.2.3-4')

        result = loose_version.get_tokens()
        self.assertEqual(result, expected)

    def test_get_tokens_other(self) -> None:
        """
        Test getting version.
        """
        expected = ['• hello ', '123', ' •']

        loose_version = command_mod.LooseVersion('hello 123')

        result = loose_version.get_tokens()
        self.assertEqual(result, expected)

    def test_get_tokens_blank(self) -> None:
        """
        Test getting version.
        """
        expected = ['• ', '', ' •']

        loose_version = command_mod.LooseVersion('')

        result = loose_version.get_tokens()
        self.assertEqual(result, expected)

    def test_sorting(self) -> None:
        """
        Test sorting.
        """
        expected = [
            '1.1',
            '1.1.2',
            '1.2a2',
            '1.2rc2',
            '1.2',
            '1.2+git20220419',
            '1.2-2',
            '1.2-2a',
            '1.2.1',
            '1.2a',
            '1.12',
            'debian11',
            'debian11.bash',
            'debian11-32',
            'debian13/',
            'debian13.bash',
            'python',
            'python3.14',
        ]

        versions = [
            '1.1.2',
            '1.12',
            '1.1',
            'debian11.bash',
            'debian11',
            '1.2',
            '1.2a2',
            '1.2a',
            '1.2rc2',
            '1.2+git20220419',
            '1.2.1',
            '1.2-2a',
            '1.2-2',
            'debian11-32',
            'debian13/',
            'debian13.bash',
            'python3.14',
            'python',
        ]

        loose_versions = [command_mod.LooseVersion(x) for x in versions]

        result = [x.get_version() for x in sorted(loose_versions)]
        self.assertEqual(result, expected)


class TestAlnumVersion(unittest.TestCase):
    """
    This class tests lnumVersion class.
    """
    def test_sorting(self) -> None:
        """
        Test sorting.
        """
        expected = [
            '1.1',
            '1.1.2',
            '1.2',
            '1.2a',
            '1.2a2',
            '1.2rc2',
            '1.2+git20220419',
            '1.2-2',
            '1.2-2a',
            '1.2.1',
            '1.12',
            'debian11',
            'debian11.bash',
            'debian11-32',
            'debian13/',
            'debian13.bash',
            'python',
            'python3.14',
        ]

        versions = [
            '1.1.2',
            '1.12',
            '1.1',
            'debian11.bash',
            'debian11',
            '1.2',
            '1.2a2',
            '1.2a',
            '1.2rc2',
            '1.2+git20220419',
            '1.2.1',
            '1.2-2a',
            '1.2-2',
            'debian11-32',
            'debian13/',
            'debian13.bash',
            'python3.14',
            'python',
        ]

        alnum_versions = [command_mod.AlnumVersion(x) for x in versions]

        result = [x.get_version() for x in sorted(alnum_versions)]
        self.assertEqual(result, expected)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        print(f"\n{__file__}:unittest.main(verbosity=2, buffer=True):")
        unittest.main(verbosity=2, buffer=True)
