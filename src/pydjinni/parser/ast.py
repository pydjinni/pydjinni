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
from pydantic import BaseModel

from pydjinni.parser.base_models import (
    BaseType,
    BaseField,
    ClassType,
    TypeReference,
    DocStrEnum,
    SymbolicConstantField,
    SymbolicConstantType,
    BaseExternalType,
    DataField

)
from pydjinni.parser.identifier import Identifier
from pydjinni.position import Position


class Namespace(BaseModel):
    comment: str | None
    name: Identifier
    position: Position
    children: list[BaseModel]


class Enum(SymbolicConstantType):
    primitive: BaseExternalType.Primitive = BaseExternalType.Primitive.enum

    class Item(SymbolicConstantField):
        ...

    items: list[Item]


class Flags(SymbolicConstantType):
    class Flag(SymbolicConstantField):
        all: bool
        none: bool

    primitive: BaseExternalType.Primitive = BaseExternalType.Primitive.flags
    flags: list[Flag]


class Parameter(BaseField):
    type_ref: TypeReference


class Interface(ClassType):
    class Method(BaseField):
        parameters: list[Parameter] = []
        return_type_ref: TypeReference | None = None
        static: bool = False
        const: bool = False
        asynchronous: bool = False
        throwing: list[TypeReference] | None = None

    class Property(BaseField):
        type_ref: TypeReference

    primitive: BaseExternalType.Primitive = BaseExternalType.Primitive.interface
    main: bool = False
    methods: list[Method] = []
    properties: list[Property] = []


class Function(BaseType):
    anonymous: bool = True
    primitive: BaseExternalType.Primitive = BaseExternalType.Primitive.function
    parameters: list[Parameter] = []
    return_type_ref: TypeReference | None = None
    targets: list[str] = []
    throwing: list[TypeReference] | None = None


class Record(ClassType):
    class Deriving(DocStrEnum):
        eq = 'eq', """
        Equality operator. 
        All fields in the record are compared in the order they appear in the record declaration. 
        If you need to add a field later, make sure the order is correct.
        """
        ord = 'ord', """
        Ordering comparison.
        Is not supported for collection types, optionals, and booleans.
        """

    primitive: BaseExternalType.Primitive = BaseExternalType.Primitive.record
    fields: list[DataField] = []
    deriving: set[Deriving] = set()

class ErrorDomain(BaseType):
    class ErrorCode(BaseType):
        parameters: list[Parameter] = []

    primitive: BaseExternalType.Primitive = BaseExternalType.Primitive.error
    error_codes: list[ErrorCode] = []
