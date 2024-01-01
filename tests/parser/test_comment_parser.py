from mistune import Markdown

from pydjinni.parser.markdown_plugins import commands_plugin


def test_markdown_plugins():
    # GIVEN a Markdown parser instance
    md = Markdown(plugins=[commands_plugin])

    # WHEN parsing the markdown input containing special commands
    tokens, state = md.parse("""hello world
@param foo bar
@param bar baz

@deprecated

@returns foo
hello world""")

    # THEN the special commands should be parsed correctly
    assert tokens[1]['type'] == "param"
    assert tokens[1]['attrs']['name'] == "foo"
    assert tokens[1]['children'][0]['raw'] == "bar"
    assert tokens[2]['type'] == "param"
    assert tokens[2]['attrs']['name'] == "bar"
    assert tokens[2]['children'][0]['raw'] == "baz"
    assert tokens[4]['type'] == "deprecated"
    assert tokens[4]['children'][0]['raw'] == ""
    assert tokens[6]['type'] == "returns"
    assert tokens[6]['children'][0]['raw'] == "foo"
