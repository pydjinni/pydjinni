from dataclasses import dataclass

from mistune import Markdown


@dataclass
class MarkdownCommand:
    name: str
    description: str
    parameter: str = None

    @property
    def pattern(self):
        return r'^ {0,3}[@\\]' + self.name + r'(?P<' + self.name + r'_command_content>([ \t\v\f]+.+)?(\n[ \t\v\f]+[^@\\].*)*)'

    @property
    def command(self):
        def parse_block_command(block, m, state):
            text = m.group(f'{self.name}_command_content').strip()
            if self.parameter and text:
                parameter_value = text.split()[0]
                text_value = text[len(parameter_value) + 1:]
                state.append_token({'type': self.name, 'text': text_value, 'attrs': {self.parameter: parameter_value}})
            else:
                state.append_token({'type': self.name, 'text': text})
            return m.end() + 1

        return parse_block_command


markdown_commands = [
    MarkdownCommand("returns", "documents the return value of a method"),
    MarkdownCommand("deprecated", "marks a type, field or method as deprecated"),
    MarkdownCommand("param", "documents a method parameter", parameter="name")
]


def commands_plugin(md: Markdown):
    for command in markdown_commands:
        md.block.register(command.name, command.pattern, command.command)
