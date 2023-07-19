import token

from pygments.lexer import RegexLexer, bygroups
from pygments.token import *


class PyDjinniLexer(RegexLexer):
    name = 'PyDjinni'
    aliases = ['pydjinni', 'djinni']
    filenames = ['*.pydjinni', '*.djinni']

    tokens = {
        'root': [
            (r'# .*\n', Comment),
            (r'(function|interface|flags|enum|record|namespace|const|property)', Keyword),
            (r'->', Punctuation),
            (r'[={};():]', Punctuation),
            (r'[+-][a-z]*', Name.Attribute),
            (r'.', Text),
        ]
    }
