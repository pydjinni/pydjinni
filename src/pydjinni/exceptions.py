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


class FileNotFoundException(ApplicationException, code=2):
    """The file could not be found"""

    def __init__(self, file: Path):
        super().__init__(str(file.absolute().as_uri()))


class InputParsingException(ApplicationException, code=140):
    """Parsing input has failed"""


class ConfigurationException(InputParsingException, code=141):
    """Error loading the configuration"""
