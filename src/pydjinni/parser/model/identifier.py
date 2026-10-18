# Copyright 2023 - 2026 jothepro
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

from pydjinni.config.model.identifier_style import IdentifierStyle, IdentifierStyleLike
lazy from pydjinni.position import Position

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, ValidatorFunctionWrapHandler


@dataclass
class Identifier:
    """Positional string value with modification helpers and case style conversion utilities."""

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
        """Add a prefix in front of an existing Identifier.

        Returns:
            Identifier: a new Identifier with the prefix prepended to it, connected by an underscore.
        """
        return Identifier(value=f"{prefix}_{self.value}", position=self.position)

    def append(self, postfix: str) -> Identifier:
        """Add a postfix at the end of an existing Identifier.

        Returns:
            Identifier: a new Identifier with the postfix appended to it, connected by an underscore.
        """
        return Identifier(value=f"{self.value}_{postfix}", position=self.position)

    def wrap(self, prefix: str, postfix: str) -> Identifier:
        """Add both a ``prefix`` and ``postfix`` to the current Identifier.

        Returns:
            Identifier: a new Identifier with both ``prefix`` and ``postfix`` added to it, connected by an underscore.
        """
        return self.prepend(prefix).append(postfix)

    def convert(self, identifier_style: IdentifierStyleLike) -> str:
        """Convert an Identifier to the specified case style.

        Args:
            identifier_style: ``IdentifierStyle`` or ``IdentifierStyle.Case`` specifying the target case style.
                   If an ``IdentifierStyle`` is given, a prefix of the output string can be specified.

        Returns:
            str: the ``value`` of the Identifier, converted to the given case style.
        """

        def convert_token(token: str, case: IdentifierStyle.Case, first: bool = False) -> str:
            match (case, first):
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

        tokens: Final = (
            tuple(
                self.value,
            )
            if identifier_style.style == IdentifierStyle.Case.none
            else tuple(self.value.split("_"))
        )

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
