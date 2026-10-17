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


from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Self

from pydantic_core import core_schema

from pydjinni.parser.model.identifier import Identifier

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, ValidatorFunctionWrapHandler


@dataclass
class NamespaceTuple:
    values: tuple[Identifier, ...] = ()

    def parent(self) -> NamespaceTuple | None:
        if len(self.values) > 0:
            return NamespaceTuple(values=self.values[:-1])

    @classmethod
    def _deserialize(cls, input: Any, validate: ValidatorFunctionWrapHandler) -> Self:
        return (
            input
            if isinstance(input, cls)
            else cls(validate(cls(values=tuple(Identifier(segment) for segment in input.split(".") if segment))))
        )

    @staticmethod
    def _serialize(namespace_tuple: NamespaceTuple) -> str:
        return ".".join(identifier.value for identifier in namespace_tuple.values)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            function=cls._deserialize,
            # TODO pick a proper regex pattern here, the current one is too lax
            schema=core_schema.str_schema(pattern=r"[\.\w]+"),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
            ),
        )
