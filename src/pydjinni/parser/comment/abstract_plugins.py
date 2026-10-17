import re
from re import Match, Pattern
from typing import Final, NamedTuple, override

from marko.block import BlockElement
from marko.element import Element
lazy from marko.source import Source


class MarkdownPlugin(Element):
    name: str
    example: str


class Command(BlockElement, MarkdownPlugin):
    priority = 10
    breaks_paragraph = True

    def __init__(self, match: Match[str]) -> None:
        self.inline_body = match.group("content").strip()

    @override
    @classmethod
    def match(cls, source: Source) -> Match[str] | None:
        pattern: Final = re.compile(
            r" {0,3}[@\\]" + cls.name + r" *(?P<content>((?:(?!\n{2,})\n?[^@])+)?)",
            flags=re.MULTILINE,
        )
        return source.expect_re(pattern)

    @override
    @classmethod
    def parse(cls, source: Source) -> Match[str] | None:
        m: Final = source.match
        source.consume()
        return m


class ParameterCommand(BlockElement, MarkdownPlugin):
    breaks_paragraph = True
    parameter: str

    class ParameterCommandInfo(NamedTuple):
        content: str
        parameter: str

    def __init__(self, parameter_command_info: ParameterCommandInfo) -> None:
        self.inline_body = parameter_command_info.content
        self.parameter = parameter_command_info.parameter

    @classmethod
    def pattern(cls) -> Pattern[str]:
        return re.compile(
            (r" {0,3}[@\\]" + cls.name + r" +(?P<parameter>([\w\.]+)) *(?P<content>((?:(?!\n{2,})\n?[^@])+)?)"),
            flags=re.MULTILINE,
        )

    @override
    @classmethod
    def match(cls, source: Source) -> Match[str] | None:
        return source.expect_re(cls.pattern())

    @override
    @classmethod
    def parse(cls, source: Source) -> ParameterCommandInfo | None:
        match: Final = source.match
        if match:
            source.consume()
            content = match.group("content").strip()
            parameter = match.group("parameter")
            return ParameterCommand.ParameterCommandInfo(content, parameter)


class TypeReferenceCommand(ParameterCommand):
    """
    Defines a command that has a type reference as first parameter
    """
