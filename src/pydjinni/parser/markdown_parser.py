# Copyright 2025 jothepro
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
from re import Match
from mistune import BlockState, Markdown

from .identifier import Identifier
from pydjinni.position import Cursor, Position

from .base_models import CommentTypeReference, TypeReference


@dataclass
class MarkdownCommand:
    name: str
    description: str

    @property
    def command_content_group(self) -> str:
        return f'{self.name}_command_content'

    @property
    def pattern(self):
        return r'^[ \t]*[@\\]' + self.name + r'(?P<' + self.command_content_group + r'>((?:(?!\n{2,})\n?[^@])+)?)$'

    @property
    def command(self):
        def parse_block_command(_, match: Match, state: BlockState):
            text = match.group(self.command_content_group)
            state.append_token({'type': self.name, 'text': text})
            return match.end() + 1
        return parse_block_command


@dataclass
class ParameterMarkdownCommand(MarkdownCommand):
    parameter: str

    @property
    def parameter_group(self) -> str:
        return f'{self.name}_parameter'


    @property
    def pattern(self):
        return r'^[ \t]*[@\\]' + self.name + r'[ \t]+(?P<' + self.parameter_group + r'>(\S+))[ \t]*(?P<' + self.command_content_group + r'>((?:(?!\n{2,})\n?[^@])+)?)$'

    
    @property
    def command(self):
        def parse_parameter_block_command(_, match: Match, state: BlockState):
            parameter = match.group(self.parameter_group)
            text = match.group(self.command_content_group)
            state.append_token({'type': self.name, 'text': text, 'attrs': {self.parameter: parameter}})
            return match.end() + 1
        return parse_parameter_block_command


@dataclass
class TypeReferenceMarkdownCommand(ParameterMarkdownCommand):
    """
    Defines a command that has a type reference as first parameter
    """
    position: Position
    namespace: list[Identifier]
    type_references: list[TypeReference]

    @property
    def command(self):
        def parse_type_parameter_block_command(_, match: Match, state: BlockState):
            parameter = match.group(self.parameter_group)
            typename = parameter.rsplit(".")[-1]
            text = match.group(self.command_content_group)
            position = Position.from_match(state.src, self.position.file, match, self.parameter_group).relative_to(self.position, column_offset=1)
            parameter_type_ref = CommentTypeReference(
                name=parameter, 
                namespace=self.namespace, 
                position=position, 
                identifier_position=position.with_offset(start=Cursor(col=len(parameter) - len(typename)))
            )
            self.type_references.append(parameter_type_ref)
            state.append_token({'type': self.name, 'text': text, 'attrs': {self.parameter: parameter_type_ref}})
            return match.end() + 1
        return parse_type_parameter_block_command

class MarkdownParser:
    def __init__(self, type_references: list[TypeReference] = []):
        self.type_references = type_references

    def commands(self, namespace: list[Identifier] = [], position: Position = None) -> list[MarkdownCommand]:
        return [
            MarkdownCommand("returns", "documents the return value of a method"),
            MarkdownCommand("deprecated", "marks a type, field or method as deprecated"),
            ParameterMarkdownCommand("param", "documents a method parameter", parameter="name"),
            TypeReferenceMarkdownCommand(
                name = "throws", 
                description = "documents an exception type that a method may throw", 
                parameter="type_ref", 
                position=position, 
                namespace=namespace,
                type_references=self.type_references
            )
        ]
            
    def parse(self, text: str | None, namespace: list[Identifier], position: Position = Position()) -> tuple[list, BlockState] | None:
        def commands_plugin(md: Markdown):
            for command in self.commands(namespace, position): md.block.register(command.name, command.pattern, command.command)

        if text:
            return Markdown(plugins=[commands_plugin]).parse(text)
        else:
            return None
