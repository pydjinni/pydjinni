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
            (r'(namespace)( *.*)({)', bygroups(Keyword, Name.Namespace, Other)),
            (r'(.* *)(= *)(record|interface|flags|enum)', bygroups(Name.Class, Operator, Keyword)),
            (r'( *property)?( *.* *)(:)( *.* *)(;|,)', bygroups(Keyword, Name.Property, Operator, Name.Class, Punctuation)),
            (r'.', Text),
        ]
    }
