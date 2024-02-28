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
from pathlib import Path

import pydantic
import yaml

from pydjinni.position import Position, Cursor

return_codes: dict[int, str] = {}


class ApplicationException(Exception):
    """Pydjinni Application Exception"""

    def __init_subclass__(cls, code: int = -1):
        if code > 0:
            cls.code = code
            assert return_codes.get(code) is None, f"The return code '{code}' is already in use!"
            return_codes[code] = cls.__doc__

    def __init__(self, description: str, position: Position = None):
        self.description = description
        self.position = position

    def __str__(self) -> str:
        output = self.__doc__
        if self.position:
            if self.position.file:
                output += f" in {self.position.file.absolute().as_uri()}"
            if self.position.start:
                output += f" at ({self.position.start.line}, {self.position.start.col})"
        output += f":\n{self.description}"
        return output

    @classmethod
    def from_yaml_error(cls, error: yaml.MarkedYAMLError):
        return cls(error.problem, Position(file=Path(error.problem_mark.name),
                                           start=Cursor(line=error.problem_mark.line, col=error.problem_mark.column)))

    @classmethod
    def from_json_error(cls, file: Path, error: json.JSONDecodeError):
        return cls(error.msg, Position(file=file, start=Cursor(line=error.lineno, col=error.colno)))

    @classmethod
    def from_pydantic_error(cls, error: pydantic.ValidationError, file: Path = None):
        outputs = []
        for error in error.errors():
            location = '.'.join([error for error in error['loc'] if "function-after" not in error])
            outputs.append(f"in key '{location}': {error['msg']}")
        joined_output = '\n'.join(outputs)
        if file:
            return cls(joined_output, position=Position(file=file))
        else:
            return cls(joined_output)


class ApplicationExceptionList(Exception):
    def __init__(self, items: list[ApplicationException]):
        self.items = items


class FileNotFoundException(ApplicationException, code=2):
    """The file or directory could not be found"""

    def __init__(self, file: Path, position: Position = None):
        super().__init__(str(file.absolute().as_uri()), position)


class UnknownTargetException(ApplicationException, code=120):
    """Unknown target"""


class ExternalCommandException(ApplicationException, code=130):
    """External command execution has failed"""

    def __init__(self, command: str):
        super().__init__(description=f"'{command}'")


class InputParsingException(ApplicationException, code=140):
    """Parsing input has failed"""


class ConfigurationException(InputParsingException, code=141):
    """Error loading the configuration"""
