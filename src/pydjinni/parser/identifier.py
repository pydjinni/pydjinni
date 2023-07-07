from typing import Any, Annotated

from pydantic import AfterValidator
from pydantic_core import core_schema

from pydjinni.config.types import IdentifierStyle


class IdentifierType(str):
    def convert(self, style: IdentifierStyle | IdentifierStyle.Case):
        def convert_token(token: str, style: IdentifierStyle.Case, first: bool = False) -> str:
            match (style, first):
                case (IdentifierStyle.Case.camel, True) | (IdentifierStyle.Case.snake, True | False) | (
                    IdentifierStyle.Case.kebab, True | False):
                    return token.lower()
                case (IdentifierStyle.Case.camel, False) | (IdentifierStyle.Case.pascal, True | False):
                    return token.capitalize()
                case (IdentifierStyle.Case.train, True | False):
                    return token.upper()
                case _:
                    return token

        identifier_style: IdentifierStyle = style if type(
            style) is IdentifierStyle else IdentifierStyle(style=style.value)

        tokens = [self] if identifier_style.style == IdentifierStyle.Case.none else self.split('_')

        match identifier_style.style:
            case IdentifierStyle.Case.train | IdentifierStyle.Case.snake:
                link = '_'
            case IdentifierStyle.Case.kebab:
                link = '-'
            case _:
                link = ''

        converted_tokens = [convert_token(tokens[0], identifier_style.style, first=True)]
        converted_tokens += [convert_token(token, identifier_style.style) for token in tokens[1:]]

        output = link.join(converted_tokens)
        if identifier_style.prefix is not None:
            output = f"{style.prefix}{output}"
        return output


Identifier = Annotated[
    str,
    AfterValidator(lambda x: IdentifierType(x)),
]
