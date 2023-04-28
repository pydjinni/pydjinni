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
            (r'(.* *)(= *)(record|interface|flags|enum)', bygroups(Name.Class, Operator, Keyword)),
            (r'(.* *)(:)( *.* *)(;|,)', bygroups(Name.Property, Operator, Name.Class, Punctuation)),
            (r'.', Text),
        ]
    }
