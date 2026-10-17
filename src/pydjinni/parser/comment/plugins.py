import re

from marko.inline import InlineElement

from pydjinni.parser.comment.abstract_plugins import (
    Command,
    MarkdownPlugin,
    ParameterCommand,
    TypeReferenceCommand,
)


class ReturnsCommand(Command):
    "documents the return value of a method"

    name = "returns"


class DeprecatedCommand(Command):
    "marks a type, field or method as deprecated"

    name = "deprecated"


class ParamCommand(ParameterCommand):
    "documents a method parameter"

    name = "param"
    parameter = "name"

    def __init__(self, parameter_command_info: ParameterCommand.ParameterCommandInfo) -> None:
        super().__init__(parameter_command_info)


class ThrowsCommand(TypeReferenceCommand):
    "documents an exception type that a method may throw"

    name = "throws"
    parameter = "reference"


class InlineReference(InlineElement, MarkdownPlugin):  # TODO how will the renderer resolve the type for linking?
    """
    Represents an inline type reference in a markdown comment.
    This is used to parse type references that are defined inline, e.g. ``type_name``.
    """

    name = "inline_type_ref"
    example = "``test``"
    priority = 8
    pattern = re.compile(r"``([\w\.]+)``")
