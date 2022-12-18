#!/usr/bin/env python3
"""
Python configuration module (uses "config_mod.yaml")

Supports BSON, multi-JSON, XML, multi-YAML files.

Copyright GPL v2: 2017-2022 By Dr Colin Kong
"""

import json
import os
import re
import xml
from pathlib import Path
from typing import (
    BinaryIO,
    Generator,
    List,
    TextIO,
    Tuple,
    Union,
)

import bson  # type: ignore
import xmltodict  # type: ignore
import yaml  # type: ignore

RELEASE = '2.0.0'
VERSION = 20221218


class Data:
    """
    This class contains de-serialized BSON/JSON/YAML data.
    """
    def __init__(self, file: Union[str, Path] = None) -> None:
        self._blocks: List[dict] = [{}]
        if file:
            self.read(Path(file))

    @staticmethod
    def _unjinja(data: str) -> str:
        """
        Replace Jinja directives.
        """
        lines = []
        for line in data.replace('\r\n', '\n').split('\n'):
            if line.startswith('{{') and line.endswith('}}'):
                if ' toYaml ' in line and ' indent ' in line:
                    indent = int(line.split(' indent ')[1].split()[0])
                    lines.append(f"{' '*(indent-2)}- {line}")
                else:
                    lines.append('')
                continue
            lines.append(re.sub(':.*{{.*:.*}}.*', ': 0', line))
        data_new = '\n'.join(lines)

        data_new = re.sub('{{[^}]*}}: *{{[^}]*}}', '_: 0', data_new)
        data_new = re.sub(':  *{{[^}]*}}', ': 0', data_new)
        data_new = re.sub('{{[^}]*}}', lambda m: ' '*len(m.group()), data_new)
        data_new = re.sub('{%[^}]*}', '', data_new)

        return data_new

    @staticmethod
    def _split_jsons(text: str) -> List[str]:
        """
        Split multiple JSONs in string and return list of JSONs.
        """
        return re.sub('}[ \\n]*{', '}}{{', text).split('}{')

    @staticmethod
    def _split_yamls(text: str) -> List[str]:
        """
        Split multiple YAMLs in string and return list of YAMLs.
        """
        return re.split('\n--', text)

    @staticmethod
    def _reformat_yaml(text: str) -> str:
        lines = []
        block = ''
        for line in text.split('\n'):
            if not block:
                if line.endswith('\\') and ': "' in line:
                    block = line.strip('\\')
                    indent = len(block) - len(block.lstrip()) + 2
                    continue
            elif line.startswith(indent*' '):
                block += line[indent:].strip('\\')
                continue
            else:
                lines.append(block.split(': "', 1)[0] + ': |')
                block = block.split(': "')[1].rstrip('"').replace('\\"', '"')
                if block.endswith('\\n'):
                    block = block[:-2]
                lines.extend([f"{indent*' '}{i}" for i in block.split('\\n')])
                block = ''

            lines.append(line)

        return '\n'.join(lines)

    def get(self) -> Generator[dict, None, None]:
        """
        Yield de-serialized data blocks.
        """
        for block in self._blocks:
            yield block

    def set(self, blocks: List[dict]) -> None:
        """
        Set de-serialized data blocks.
        """
        self._blocks = blocks

    def add(self, block: dict) -> None:
        """
        Add de-serialized data block.
        """
        self._blocks.append(block)

    @classmethod
    def _decode_json(cls, data: str) -> List[str]:
        try:
            blocks = [json.loads(block) for block in cls._split_jsons(data)]
        except json.decoder.JSONDecodeError as exception:
            raise ReadConfigError(exception) from exception
        return blocks

    @classmethod
    def _decode_yaml(cls, data: str) -> List[str]:
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

    def read(self, path: Path, check: bool = False) -> None:
        """
        Read or check configuration file.
        """
        ifile: Union[TextIO, BinaryIO]

        try:
            if path.suffix == '.bson':
                try:
                    with path.open('rb') as ifile:
                        blocks = [bson.decode(  # pylint: disable=no-member
                            ifile.read(),
                        )]
                except IndexError as exception:
                    raise ReadConfigError(exception) from exception
            elif path.suffix == '.xml':
                try:
                    with path.open('rb') as ifile:
                        blocks = [xmltodict.parse(
                            ifile.read(),
                            dict_constructor=dict,
                        )]
                except xml.parsers.expat.ExpatError as exception:
                    raise ReadConfigError(exception) from exception
            else:
                with path.open(encoding='utf-8') as ifile:
                    data = ifile.read()
                if check:
                    data = self._unjinja(data)
                if path.suffix == '.json':
                    blocks = self._decode_json(data)
                elif path.suffix in ('.yaml', '.yml'):
                    blocks = self._decode_yaml(data)
                else:
                    raise ReadConfigError("Cannot handle configuration file.")
        except OSError as exception:
            raise ReadConfigError(
                f"Cannot read configuration file: {path}",
            ) from exception
        if not check:
            self._blocks = blocks

    def write(self, path: Path, compact: bool = False) -> None:
        """
        Write configuration file
        """
        tmp_path = Path(f'{path}.part{os.getpid()}')
        ofile: Union[TextIO, BinaryIO]

        try:
            if path.suffix == '.json':
                with tmp_path.open(
                    'w',
                    encoding='utf-8',
                    newline='\n',
                ) as ofile:
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
            elif path.suffix in ('.yaml', '.yml'):
                yaml_data = [
                    self._reformat_yaml(yaml.dump(
                        block,
                        allow_unicode=True,
                        indent=2,
                    ))
                    for block in self._blocks
                ]
                with tmp_path.open(
                    'w',
                    encoding='utf-8',
                    newline='\n',
                ) as ofile:
                    print('--\n'.join(yaml_data), end='', file=ofile)
            elif path.suffix == '.bson':
                if len(self._blocks) > 1:
                    raise WriteConfigError(
                        f'Cannot handle multi-writes to "{tmp_path}" file.',
                    )
                with tmp_path.open('wb') as ofile:
                    ofile.write(bson.encode(  # pylint: disable=no-member
                        self._blocks[0],
                    ))
            else:
                raise WriteConfigError(f'Cannot handle "{tmp_path}" file.')
        except OSError as exception:
            raise WriteConfigError(
                f'Cannot create "{tmp_path}" file.',
            ) from exception

        tmp_path.replace(path)


class Config:
    """
    This class deals with "config_mod.yaml" configuration file.
    """
    def __init__(self) -> None:
        path = Path(Path(__file__).parent, 'config_mod.yaml')
        mappings = next(Data(path).get())
        self._apps = mappings.get('apps', {})
        self._bindings = mappings.get('bindings', {})
        self._parameters = mappings.get('parameters', {})

    def get(self, parameter: str) -> str:
        """
        Return parameter or None
        """
        return self._parameters.get(parameter)

    def get_app(
        self,
        app_name: str,
        view: bool = False,
    ) -> Tuple[List[str], bool]:
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

    def get_open_app(self, extension: str) -> Tuple[List[str], bool]:
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(extension, {}).get('open')
        if app_name:
            return self.get_app(app_name)

        return None

    def get_view_app(self, extension: str) -> Tuple[List[str], bool]:
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
