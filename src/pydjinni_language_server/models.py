from dataclasses import dataclass
from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel
from pydjinni.defs import DEFAULT_CONFIG_PATH
from pydjinni.exceptions import ApplicationException
from pydjinni.parser.ast import Namespace
from pydjinni.parser.base_models import BaseField, BaseType, TypeReference
from pydjinni.position import Position


class Configuration(BaseModel, alias_generator=to_camel):
    debug_logs: bool = False
    config: Path = DEFAULT_CONFIG_PATH
    generate_on_save: bool = False

    @staticmethod
    def from_response(responses: list[dict[str, Any]]) -> list["Configuration"]:
        return [Configuration.model_validate(response) for response in responses]


@dataclass
class Diagnostics:

    @dataclass
    class DiagnosticItem:
        definition: BaseType | TypeReference | BaseField | Namespace | ApplicationException
        message: str

    errors: list[DiagnosticItem]
    warnings: list[DiagnosticItem]


@dataclass
class GeneratedSource:
    language: str
    uri: str
    type_def: BaseType


@dataclass
class ReferenceLocationLink:
    target_position: Position
    target_selection: Position
    origin_position: Position
