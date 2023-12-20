from mistune import Markdown


def commands_plugin(md: Markdown):
    def pattern(keyword: str) -> str:
        return r'^ {0,3}[@\\]' + keyword + r'(?P<' + keyword + r'_command_content>([ \t\v\f]+.+)?(\n[ \t\v\f]+[^@\\].*)*)'

    def commands_block_command(keyword: str, parameter: str = None):
        def parse_block_command(block, m, state):
            text = m.group(f'{keyword}_command_content').strip()
            if parameter and text:
                parameter_value = text.split()[0]
                text_value = text[len(parameter_value) + 1:]
                state.append_token({'type': keyword, 'text': text_value, 'attrs': {parameter: parameter_value}})
            else:
                state.append_token({'type': keyword, 'text': text})
            return m.end() + 1
        return parse_block_command

    md.block.register('returns', pattern("returns"), commands_block_command('returns'))
    md.block.register('deprecated', pattern("deprecated"), commands_block_command('deprecated'))
    md.block.register('param', pattern("param"), commands_block_command('param', 'name'))



