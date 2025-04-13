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

from __future__ import annotations
from pathlib import Path

from mistune import BlockState
from pydantic.json_schema import SkipJsonSchema
from pydjinni.parser.identifier import Identifier
from pydjinni.parser.namespace import Namespace
from pydjinni.position import Position

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11
from pydantic import BaseModel, Field, PrivateAttr, SkipValidation, computed_field


class DocStrEnum(StrEnum):
    def __new__(cls, value, doc=None):
        member = str.__new__(cls, value)
        member._value_ = value
        member.__doc__ = doc.strip()
        return member


class BaseCommentModel(BaseModel):
    comment: str | None = Field(
        default=None,
        description="A short description of the type"
    )
    deprecated: str | bool = Field(
        default=False,
        description="Marks a type as deprecated"
    )
    _parsed_comment: tuple[list, BlockState] = PrivateAttr(default=None)

class BaseExternalType(BaseCommentModel):
    class Primitive(StrEnum):
        primitive = 'primitive'
        collection = 'collection'
        interface = 'interface'
        record = 'record'
        enum = 'enum'
        flags = 'flags'
        function = 'function'
        error = 'error'

    name: Identifier = Field(
        description="Name of the type in the IDL"
    )
    namespace: list[Identifier] = Field(
        default=[],
        description="Namespace that the type lives in"
    )
    primitive: Primitive = Field(
        default=Primitive.primitive,
        description="The underlying primitive type"
    )
    params: list[str] = []
    position: SkipJsonSchema[Position | None] = Field(exclude=True, default=None)


class TypeReference(BaseModel):
    name: Identifier
    namespace: Namespace | list[Identifier] = []
    position: Position = Position()
    parameters: list[TypeReference] = []
    optional: bool = False
    type_def: BaseExternalType = Field(
        default=None,
        repr=False
    )

class CommentTypeReference(TypeReference):
    pass

class FileReference(BaseModel):
    path: Path
    position: Position

class BaseType(BaseExternalType, extra='allow'):
    dependencies: list[TypeReference] = []


class BaseField(BaseCommentModel, extra='allow'):
    name: Identifier
    position: Position = None


class ClassType(BaseType):
    targets: list[str] = []


class SymbolicConstantField(BaseField):
    pass


class SymbolicConstantType(BaseType):
    pass

class DataField(BaseField):
    type_ref: TypeReference
