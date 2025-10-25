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

from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, PlainSerializer, WithJsonSchema
from pydantic_core import core_schema

from pydjinni.config.types import IdentifierStyle


class IdentifierType(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(cls, core_schema.str_schema())

    def prepend(self, prefix: str) -> "IdentifierType":
        return IdentifierType(f"{prefix}_{self}")

    def append(self, postfix: str) -> "IdentifierType":
        return IdentifierType(f"{self}_{postfix}")

    def wrap(self, prefix: str, postfix: str) -> "IdentifierType":
        return self.prepend(prefix).append(postfix)

    def convert(self, style: IdentifierStyle | IdentifierStyle.Case):
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

        identifier_style: IdentifierStyle = (
            style if isinstance(style, IdentifierStyle) else IdentifierStyle(style=style)
        )

        tokens = [self] if identifier_style.style == IdentifierStyle.Case.none else self.split("_")

        match identifier_style.style:
            case IdentifierStyle.Case.train | IdentifierStyle.Case.snake:
                link = "_"
            case IdentifierStyle.Case.kebab:
                link = "-"
            case _:
                link = ""

        converted_tokens = [convert_token(tokens[0], identifier_style.style, first=True)]
        converted_tokens += [convert_token(token, identifier_style.style) for token in tokens[1:]]
        return f"{identifier_style.prefix}{link.join(converted_tokens)}"


IdentifierField = Annotated[
    IdentifierType,
    AfterValidator(lambda x: IdentifierType(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string", "pattern": r"[_\w]+"}, mode="validation"),
]
