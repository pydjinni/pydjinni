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
from itertools import chain
from typing import TYPE_CHECKING, Any, Final, Self

from pydantic_core import core_schema

from pydjinni.config.types import IdentifierStyle
lazy from pydjinni.position import Position

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, ValidatorFunctionWrapHandler


@dataclass
class Identifier:
    value: str
    position: Position | None = None

    @classmethod
    def _deserialize(cls, input: Any, validate: ValidatorFunctionWrapHandler) -> Self:
        return input if isinstance(input, cls) else cls(validate(input))

    @staticmethod
    def _serialize(identifier: Identifier) -> str:
        return identifier.value

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            function=cls._deserialize,
            schema=core_schema.str_schema(
                pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$",
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
            ),
        )

    def prepend(self, prefix: str) -> Identifier:
        return Identifier(value=f"{prefix}_{self.value}", position=self.position)

    def append(self, postfix: str) -> Identifier:
        return Identifier(value=f"{self.value}_{postfix}", position=self.position)

    def wrap(self, prefix: str, postfix: str) -> Identifier:
        return self.prepend(prefix).append(postfix)

    def convert(self, style: IdentifierStyle | IdentifierStyle.Case) -> str:
        def convert_token(token: str, style: IdentifierStyle.Case, first: bool = False) -> str:
            match (style, first):
                case (
                    (IdentifierStyle.Case.camel, True)
                    | (IdentifierStyle.Case.snake, True | False)
                    | (IdentifierStyle.Case.kebab, True | False)
                ):
                    return token.lower()
                case (IdentifierStyle.Case.camel, False) | (IdentifierStyle.Case.pascal, True | False):
                    return token.capitalize()
                case (IdentifierStyle.Case.train, True | False):
                    return token.upper()
                case _:
                    return token

        identifier_style: Final = style if isinstance(style, IdentifierStyle) else IdentifierStyle(style=style)

        tokens: Final = (self.value,) if identifier_style.style == IdentifierStyle.Case.none else self.value.split("_")

        match identifier_style.style:
            case IdentifierStyle.Case.train | IdentifierStyle.Case.snake:
                link = "_"
            case IdentifierStyle.Case.kebab:
                link = "-"
            case _:
                link = ""

        converted_identifier: Final = link.join(
            chain(
                (convert_token(tokens[0], identifier_style.style, first=True),),
                (convert_token(token, identifier_style.style) for token in tokens[1:]),
            )
        )
        return identifier_style.prefix + converted_identifier
