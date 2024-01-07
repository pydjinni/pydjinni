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

from pydjinni.parser.base_models import TypeReference


def quote(header: Path):
    return header if str(header).startswith("<") and str(header).endswith(">") else f'"{header.as_posix()}"'


def headers(dependencies: list[TypeReference], target: str) -> list[str]:
    header_paths: list[Path] = []
    for dependency_def in dependencies:
        target_type_def = getattr(dependency_def.type_def, target)
        if hasattr(target_type_def, 'base_type') and target_type_def.base_type and hasattr(target_type_def, 'derived_header'):
            header_path = target_type_def.derived_header
        else:
            header_path = target_type_def.header
        if header_path and (header_path not in header_paths):
            header_paths.append(header_path)
    return [quote(header) for header in header_paths]
