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

from pathlib import Path

from pydantic import BaseModel, Field, create_model
from pydantic.fields import FieldInfo


class ProcessedFiles(BaseModel):
    class ParsedFiles(BaseModel):
        """List of input files that have been parsed. This does not include the config file."""
        idl: list[Path] = Field(
            default=[]
        )
        external_types: list[Path] = Field(
            default=[]
        )

    parsed: ParsedFiles = ParsedFiles()


class ProcessedFilesModelBuilder:
    def __init__(self):
        self._generated_fields: dict[str, tuple[bool, bool]] = {}

    def add_generated_field(self, key: str, header: bool = True, source: bool = True):
        self._generated_fields[key] = (header, source)

    def build(self):
        generated_files_model = self._generated_files_model()
        generated_files_model.__doc__ = "List of generated files from all registered generators"
        return create_model(
            "ProcessedFiles",
            __base__=ProcessedFiles,
            generated=(generated_files_model, generated_files_model())
        )

    def _generated_files_model(self):
        def key_model(key: str, fields: tuple[bool, bool]):
            fields_kwargs = {}
            if fields[0]:
                fields_kwargs["include_dir"] = (Path, FieldInfo(
                    default=Path(),
                    description=f"Path where all {key} header files are written to."
                ))
                fields_kwargs["header"] = (list[Path], FieldInfo(
                    default=[],
                    description=f"List of generated {key} header files."
                ))
            if fields[1]:
                fields_kwargs["source"] = (list[Path], FieldInfo(
                    default=[],
                    description=f"List of generated {key} source files."
                ))
                fields_kwargs["source_dir"] = (Path, FieldInfo(
                    default=Path(),
                    description=f"Path where all {key} source files are written to."
                ))
            return create_model(
                f"Generated_{key}",
                **fields_kwargs
            )

        field_kwargs = {}
        for key, fields in self._generated_fields.items():
            model = key_model(key, fields)
            field_kwargs[key] = (model, model())
        return create_model(
            "Generated",
            **field_kwargs
        )
