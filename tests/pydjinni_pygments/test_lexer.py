from textwrap import dedent
from typing import Final

from pygments import lex
from pygments.token import Token

from pydjinni_pygments import PyDjinniLexer


def test_lexer():
    input: Final = dedent(
        """
        foo = record {}
        """
    )
    lexed = tuple(lex(input, PyDjinniLexer()))

    assert lexed == (
        (Token.Name.Class, "foo"),
        (Token.Whitespace, " "),
        (Token.Operator, "="),
        (Token.Text, " "),
        (Token.Keyword.Type, "record"),
        (Token.Text, " "),
        (Token.Punctuation, "{"),
        (Token.Punctuation, "}"),
        (Token.Text.Whitespace, "\n"),
    )
