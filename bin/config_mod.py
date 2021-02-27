#!/usr/bin/env python3
"""
Python configuration module (uses "config_mod.yaml")

Supports BSON, multi-JSON, XML, multi-YAML files.

Copyright GPL v2: 2017-2021 By Dr Colin Kong
"""

import json
import os
import re
import shutil
import xml

import bson
import xmltodict
import yaml

RELEASE = '1.6.0'
VERSION = 20210227


class Data:
    """
    This class contains de-serialized BSON/JSON/YAML data.
    """
    def __init__(self, file=None):
        self._blocks = [{}]
        if file:
            self.read(file)

    @staticmethod
    def _unjinja(data):
        """
        Replace Jinja directives.
        """
        lines = []
        for line in data.replace('\r\n', '\n').split('\n'):
            if line.startswith('{{') and line.endswith('}}'):
                if ' toYaml ' in line and ' indent ' in line:
                    indent = int(line.split(' indent ')[1].split()[0])
                    lines.append("{0:s}- {1:s}".format(' '*(indent-2), line))
                else:
                    lines.append('')
                continue
            lines.append(line)
        data_new = '\n'.join(lines)

        data_new = re.sub('{{[^}]*}}: *{{[^}]*}}', '_: _', data_new)
        data_new = re.sub('{{[^}]*}}', lambda m: ' '*len(m.group()), data_new)
        data_new = re.sub('{%[^}]*}', '', data_new)

        return data_new

    @staticmethod
    def _split_jsons(text):
        """
        Split multiple JSONs in string and return list of JSONs.
        """
        return re.sub('}[ \\n]*{', '}}{{', text).split('}{')

    @staticmethod
    def _split_yamls(text):
        """
        Split multiple YAMLs in string and return list of YAMLs.
        """
        return re.split('\n--', text)

    def get(self):
        """
        Yield de-serialized data blocks.
        """
        for block in self._blocks:
            yield block

    def set(self, blocks):
        """
        Set de-serialized data blocks.
        """
        self._blocks = blocks

    def add(self, block):
        """
        Add de-serialized data block.
        """
        self._blocks.append(block)

    @classmethod
    def _decode_json(cls, data):
        try:
            blocks = [json.loads(block) for block in cls._split_jsons(data)]
        except json.decoder.JSONDecodeError as exception:
            raise ReadConfigError(exception) from exception
        return blocks

    @classmethod
    def _decode_yaml(cls, data):
        try:
            blocks = [
                yaml.safe_load(block) for block in cls._split_yamls(data)
            ]
        except (
                yaml.parser.ParserError,
                yaml.scanner.ScannerError,
        ) as exception:
            raise ReadConfigError(exception) from exception
        return blocks

    def read(self, file, check=False):
        """
        Read or check configuration file.
        """
        try:
            if file.endswith('bson'):
                try:
                    with open(file, 'rb') as ifile:
                        blocks = [bson.loads(ifile.read())]
                except IndexError as exception:
                    raise ReadConfigError(exception) from exception
            elif file.endswith('xml'):
                try:
                    with open(file, 'rb') as ifile:
                        blocks = [xmltodict.parse(
                            ifile.read(),
                            dict_constructor=dict,
                        )]
                except xml.parsers.expat.ExpatError as exception:
                    raise ReadConfigError(exception) from exception
            else:
                with open(file) as ifile:
                    data = ifile.read()
                if check:
                    data = self._unjinja(data)
                if file.endswith(('.json')):
                    blocks = self._decode_json(data)
                elif file.endswith(('.yml', '.yaml')):
                    blocks = self._decode_yaml(data)
                else:
                    raise ReadConfigError("Cannot handle configuration file.")
        except OSError as exception:
            raise ReadConfigError(
                "Cannot read configuration file."
            ) from exception
        if not check:
            self._blocks = blocks

    def write(self, file, compact=False):
        """
        Write configuration file
        """
        tmpfile = file + '.part' + str(os.getpid())

        try:
            if file.endswith('json'):
                with open(tmpfile, 'w', newline='\n') as ofile:
                    for block in self._blocks:
                        if compact:
                            print(
                                json.dumps(block, ensure_ascii=False),
                                file=ofile,
                            )
                        else:
                            print(json.dumps(
                                block,
                                ensure_ascii=False,
                                indent=4,
                                sort_keys=True,
                            ), file=ofile)
            elif file.endswith(('.yml', '.yaml')):
                yaml_data = [
                    yaml.dump(block, indent=2, default_flow_style=False)
                    for block in self._blocks
                ]
                with open(tmpfile, 'w', newline='\n') as ofile:
                    print('--\n'.join(yaml_data), end='', file=ofile)
            elif file.endswith('bson'):
                if len(self._blocks) > 1:
                    raise WriteConfigError(
                        'Cannot handle multi-writes to "' + tmpfile + '" file.'
                    )
                with open(tmpfile, 'wb') as ofile:
                    ofile.write(bson.dumps(self._blocks[0]))
            else:
                raise WriteConfigError('Cannot handle "' + tmpfile + '" file.')
        except OSError as exception:
            raise WriteConfigError(
                'Cannot create "' + tmpfile + '" file.'
            ) from exception

        try:
            shutil.move(tmpfile, file)
        except OSError as exception:
            raise WriteConfigError(
                'Cannot rename "' + tmpfile + '" file to "' + file + '".'
            ) from exception


class Config:
    """
    This class deals with "config_mod.yaml" configuration file.
    """
    def __init__(self):
        file = os.path.join(os.path.dirname(__file__), 'config_mod.yaml')
        mappings = next(Data(file).get())
        self._apps = mappings.get('apps', {})
        self._bindings = mappings.get('bindings', {})
        self._parameters = mappings.get('parameters', {})

    def get(self, parameter):
        """
        Return parameter or None
        """
        return self._parameters.get(parameter)

    def get_app(self, app_name, view=False):
        """
        Return (command, daemon_flag) or None
        """
        app = self._apps.get(app_name)
        if app_name:
            command = app['command']
            if view and 'view_flag' in app:
                command.append(app['view_flag'])
            daemon = app.get('daemon') is True
            return command, daemon

        return None

    def get_open_app(self, extension):
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(extension, {}).get('open')
        if app_name:
            return self.get_app(app_name)

        return None

    def get_view_app(self, extension):
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(extension, {}).get('view')
        if app_name:
            return self.get_app(app_name, view=True)

        return None


class ConfigError(Exception):
    """
    Config module error.
    """


class ReadConfigError(ConfigError):
    """
    Read config file error.
    """


class WriteConfigError(ConfigError):
    """
    Write config file error.
    """


if __name__ == '__main__':
    help(__name__)
