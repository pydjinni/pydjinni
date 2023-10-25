# Copyright 2023 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import shutil
from pathlib import Path

import tomli_w
import yaml

from pydjinni.exceptions import ConfigurationException
from pydjinni.file.processed_files_model_builder import ProcessedFiles


class FileReaderWriter:
    """
    use this class to write a generated file. This way the writing will be recorded and the generated file will be
    added to the list of generated files.
    """

    def __init__(self):
        self._processed_files = None
        self._used_keys: list[str] = []

    def setup(self, processed_files_model: type[ProcessedFiles]):
        self._processed_files = processed_files_model().model_copy(deep=True)

    def setup_include_dir(self, key: str, include_dir: Path):
        generator = getattr(self.processed_files.generated, key)
        generator.include_dir = include_dir

    def setup_source_dir(self, key: str, source_dir: Path):
        generator = getattr(self.processed_files.generated, key)
        generator.source_dir = source_dir

    @property
    def processed_files(self) -> ProcessedFiles:
        return self._processed_files

    def read_idl(self, filename: Path, append: bool = True) -> str:
        if append:
            self.processed_files.parsed.idl.append(filename)
        return filename.read_text()

    def read_external_type(self, filename: Path, append: bool = True) -> str:
        if append:
            self.processed_files.parsed.external_types.append(filename)
        return filename.read_text()

    def write_source(self, key: str, filename: Path, content: str, append: bool = True):
        self._write(filename, content)
        if append:
            generator = getattr(self.processed_files.generated, key)
            generator.source.append(filename)
            self._used_keys.append(key)

    def write_header(self, key: str, filename: Path, content: str, append: bool = True):
        self._write(filename, content)
        if append:
            generator = getattr(self.processed_files.generated, key)
            generator.header.append(filename)
            self._used_keys.append(key)

    def _write(self, filename: Path, content: str):
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(content)

    def _copy(self, source_file: Path, target_file: Path):
        target_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(source_file, target_file)

    def copy_source_directory(self, key: str, source_dir: Path, target_dir: Path, append: bool = True):
        if source_dir.exists():
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    target_file_path = target_dir / file_path.relative_to(source_dir)
                    self._copy(file_path, target_file_path)
                    if append:
                        generator = getattr(self.processed_files.generated, key)
                        generator.source.append(target_file_path)
                        self._used_keys.append(key)

    def copy_header_directory(self, key: str, header_dir: Path, target_dir: Path, append: bool = True):
        if header_dir.exists():
            for file_path in header_dir.rglob('*'):
                if file_path.is_file():
                    target_file_path = target_dir / file_path.relative_to(header_dir)
                    self._copy(file_path, target_file_path)
                    if append:
                        generator = getattr(self.processed_files.generated, key)
                        generator.header.append(target_file_path)
                        self._used_keys.append(key)

    def write_processed_files(self, filename: Path):
        model_dump = self._processed_files.model_dump(mode='json')

        # remove all target keys from the resulting dict that have not been used during generation.
        # The resulting output file should only contain non-empty items.
        used_keys = set(self._used_keys)
        for key in list(model_dump['generated'].keys()):
            if key not in used_keys:
                del model_dump['generated'][key]

        match filename.suffix:
            case '.yaml' | '.yml':
                file_content = yaml.dump(model_dump)
            case '.json':
                file_content = json.dumps(model_dump, indent=2)
            case '.toml':
                file_content = tomli_w.dumps(model_dump)
            case _:
                raise ConfigurationException(f"Unknown out-file extension: '{filename.suffix}'")

        self._write(filename, file_content)
