#!/usr/bin/env python3
"""
Python configuration module (uses "config_mod.yaml")

Supports BSON, multi-JSON, XML, multi-YAML files.

Copyright GPL v2: 2017-2024 By Dr Colin Kong
"""

import json
import os
import re
import sys
import xml
import xml.dom.minidom
from pathlib import Path
from typing import Any, Generator, List, Tuple, Union

import bson  # type: ignore
import dicttoxml  # type: ignore
import xmltodict  # type: ignore
import yaml  # type: ignore

RELEASE = '2.4.1'
VERSION = 20241026


class Data:
    """
    This class contains de-serialized BSON/JSON/YAML data.
    """
    TYPES = {
        '.bson': 'BSON',
        '.htm': 'XML',
        '.html': 'XML',
        '.json': 'JSON',
        '.wsdl': 'XML',
        '.xhtml': 'XML',
        '.xml': 'XML',
        '.yaml': 'YAML',
        '.yml': 'YAML',
    }

    def __init__(self, file: Union[str, Path] = None) -> None:
        self._blocks: List[dict] = [{}]
        if file:
            self.read(file)

    def get(self) -> Generator[dict, None, None]:
        """
        Yield de-serialized data blocks.
        """
        yield from self._blocks

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

    @staticmethod
    def _unjinja(data: str) -> str:
        """
        Replace Jinja directives.
        """
        lines = []
        for line in data.split('\n'):
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

    @classmethod
    def _decode_json(cls, data: str, check: bool = False) -> List[dict]:
        if check:
            data = cls._unjinja(data)
        try:
            blocks = [json.loads(block) for block in cls._split_jsons(data)]
        except json.decoder.JSONDecodeError as exception:
            raise ReadConfigError(exception) from exception
        return blocks

    @staticmethod
    def _split_yamls(text: str) -> List[str]:
        """
        Split multiple YAMLs in string and return list of YAMLs.
        """
        return re.split('\n--', text)

    @classmethod
    def _decode_yaml(cls, data: str, check: bool = False) -> List[dict]:
        if check:
            data = cls._unjinja(data)
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

    @classmethod
    def _parse_xml(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        mytype = data.get('@type')
        if data.get('#text'):
            if mytype == 'float':
                item = float(data.get('#text'))
            elif mytype == 'int':
                item = int(data.get('#text'))
            elif mytype == 'bool':
                item = bool(data.get('#text'))
            else:
                item = data.get('#text')
            return item
        if mytype == 'list':
            items = [y for x, y in data.items() if x != '@type'][0]
            if isinstance(items, list):
                return [cls._parse_xml(x) for x in items]
            return [cls._parse_xml(items)]
        if mytype == 'dict':
            data.update({
                x.pop('@name', 'key'): cls._parse_xml(x)
                for x in data.pop('key', [])
            })
        return {k: cls._parse_xml(v) for k, v in data.items() if k != '@type'}

    @classmethod
    def _decode_xml(cls, data: str) -> List[dict]:
        try:
            block = xmltodict.parse(data, dict_constructor=dict)
        except xml.parsers.expat.ExpatError as exception:
            raise ReadConfigError(exception) from exception
        block = (
            cls._parse_xml(block['root'])
            if block.get('root')
            else cls._parse_xml(block)
        )
        return [block]

    @staticmethod
    def _decode_bson(bdata: bytes) -> List[dict]:
        try:
            blocks = [bson.decode(bdata)]
        except IndexError as exception:
            raise ReadConfigError(exception) from exception
        return blocks

    def decode(
        self,
        config: str,
        data: bytes,
        check: bool = False,
    ) -> List[dict]:
        """
        Decode data and return dict.
        """
        if config == 'BSON':
            blocks = self._decode_bson(data)
        elif config == 'JSON':
            blocks = self._decode_json(data.decode(errors='replace'), check)
        elif config == 'XML':
            blocks = self._decode_xml(data.decode(errors='replace'))
        elif config == 'YAML':
            blocks = self._decode_yaml(data.decode(errors='replace'), check)
        else:
            raise ConfigError(
                f'Cannot handle decoding "{config}" format.',
            )
        return blocks

    def read(
        self,
        file: Union[str, Path],
        config: str = None,
        check: bool = False,
    ) -> None:
        """
        Read or check configuration file.
        """
        path = Path(file)
        if not config:
            config = self.TYPES.get(path.suffix)
        if not config:
            raise ReadConfigError(f'Cannot handle reading "{path}" file.')

        try:
            data = Path(file).read_bytes()
        except OSError as exception:
            raise ReadConfigError(
                f'Cannot read "{path}" {config} file.',
            ) from exception
        blocks = self.decode(config, data)
        if not check:
            self._blocks = blocks

    @staticmethod
    def _encode_json(blocks: List[dict], compact: bool) -> bytes:
        indent = None if compact else 4
        data = '\n'.join([
            json.dumps(x, ensure_ascii=False, indent=indent, sort_keys=True)
            for x in blocks
        ])
        return data.encode()

    @staticmethod
    def _reformat_yaml(text: str) -> str:
        lines = []
        block = ''
        indent = 0
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

    @classmethod
    def _encode_yaml(cls, blocks: List[dict]) -> bytes:
        data = '--\n'.join([
            cls._reformat_yaml(yaml.dump(x, allow_unicode=True, indent=2))
            for x in blocks
        ])
        return data.encode()

    @staticmethod
    def _encode_xml(block: dict, compact: bool) -> bytes:
        root = len(block) > 1
        data = dicttoxml.dicttoxml(block, root=root)
        if not compact:
            xml_doc = xml.dom.minidom.parseString(data)
            data = xml_doc.toprettyxml(
                indent='  ',
                newl='\n',
                encoding='utf-8',
            )
        return data

    @staticmethod
    def _encode_bson(block: dict) -> bytes:
        data = bson.encode(block)  # pylint: disable=no-member
        return data

    def encode(
        self,
        config: str,
        blocks: List[dict] = None,
        compact: bool = False,
    ) -> bytes:
        """
        Encode data blocks and return str.
        """
        if not blocks:
            blocks = self._blocks
        if config == 'JSON':
            data = self._encode_json(blocks, compact)
        elif config in 'YAML':
            data = self._encode_yaml(blocks)
        elif len(blocks) > 1:
            raise WriteConfigError(
                f'Cannot handle multi-encoded {config} data.',
            )
        elif config in ('XML'):
            data = self._encode_xml(blocks[0], compact)
        elif config == 'BSON':
            data = self._encode_bson(blocks[0])
        else:
            raise ConfigError(f'Cannot handle encoding "{config}" data.')
        return data

    def write(
        self,
        file: Union[str, Path],
        compact: bool = False,
        config: str = None,
    ) -> None:
        """
        Write configuration file
        """
        path = Path(file)
        tmp_path = Path(f'{path}.part{os.getpid()}')

        if not config:
            config = self.TYPES.get(path.suffix)
        if not config:
            raise WriteConfigError(f'Cannot handle writing "{path}" file.')

        data = self.encode(config, self._blocks, compact)
        try:
            tmp_path.write_bytes(data)
        except OSError as exception:
            raise WriteConfigError(
                f'Cannot create "{tmp_path}" {config} file.',
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
        app = self._apps.get(app_name.lower())
        if not app:
            raise ConfigError(
                f'Undefined "{app_name.lower()}" app in configuration.'
            )

        command = app['command']
        if view and 'view_flag' in app:
            command.append(app['view_flag'])
        daemon = app.get('daemon') is True
        return command, daemon

    def get_open_app(self, suffix: str) -> Tuple[List[str], bool]:
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(suffix.lower(), {}).get('open')
        if app_name:
            return self.get_app(app_name)

        return None

    def get_view_app(self, suffix: str) -> Tuple[List[str], bool]:
        """
        Return (command, daemon_flag) or None
        """
        app_name = self._bindings.get(suffix.lower(), {}).get('view')
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
    if sys.argv[-1] in ('-v', '-V', '-version', '--version'):
        print(f"Python configuration module {RELEASE} ({VERSION})")
    else:
        help(__name__)
