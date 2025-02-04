# Copyright 2023 jothepro
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

from pygments.lexer import RegexLexer, words, bygroups
from pygments.token import *


class PyDjinniLexer(RegexLexer):
    name = 'PyDjinni'
    aliases = ['pydjinni', 'djinni']
    filenames = ['*.pydjinni', '*.djinni']

    tokens = {
        'root': [
            (r'#', Comment, 'comment'), #comment
            (r'@import|@extern', Keyword.Reserved), #import
            (r'".*"', String.Double), #string
            (r'(?<=\=)(\s*)(all|none)', bygroups(Whitespace, Name.Builtin)), #enum_modifiers
            (words(('interface', 'enum', 'record', 'flags', 'error', 'function', 'namespace'), prefix=r'\b', suffix=r'\b'), Keyword.Type), #types
            (words(('const', 'static', 'async', 'throws', 'main'), prefix=r'\b', suffix=r'\b'), Keyword.Reserved), #modifiers
            (r'\b(deriving)(\s*)(\()', bygroups(Keyword.Reserved, Whitespace, Punctuation), 'deriving_targets'), #deriving_targets
            (r'([_\w]+)(\s*)(?=:|\(|=\s*all|=\s*none|;)', bygroups(Name, Whitespace)), #parameter
            (r'([_\w]+)(\s*)(?=\=)', bygroups(Name.Class, Whitespace)), #typename
            (r'(?<=:)(\s*)([<>_\w]+)', bygroups(Whitespace, Name.Class)), #typename_reference_parameter
            (r'(?<=->)(\s*)([<>_\w]+)', bygroups(Whitespace, Name.Class)), #typename_reference_return
            (r'(?<=\.)([<>_\w]+)', Name.Class), #typename_reference_namespace
            (r'(?<=throws)(\s*)([<>_\w]+)(\s*)(?=,)', bygroups(Whitespace, Name.Class, Whitespace)), #typename_reference_throws_1
            (r'(?<=throws)(\s*)([<>_\w]+)(\s*)(?=->)', bygroups(Whitespace, Name.Class, Whitespace)), #typename_reference_throws_2
            (r'(?<=throws)(\s*)([<>_\w]+)(\s*)(?=;)', bygroups(Whitespace, Name.Class, Whitespace)), #typename_reference_throws_3
            (r'(?<=,)(\s*)([<>_\w]+)(\s*)(?=,)', bygroups(Whitespace, Name.Class, Whitespace)), #typename_reference_throws_4
            (r'(?<=,)(\s*)([<>_\w]+)(\s*)(?=->)', bygroups(Whitespace, Name.Class, Whitespace)), #typename_reference_throws_5
            (r'(?<=,)(\s*)([<>_\w]+)(\s*)(?=;)', bygroups(Whitespace, Name.Class, Whitespace)), #typename_reference_throws_6
            (r'(?<=namespace)(\s*)([_\w]+)', bygroups(Whitespace, Name.Namespace)), #namespace_typename
            (r'\+[\w]+', Name.Tag), #interface_targets
            (r';|{|}|,|\.|\(|\)', Punctuation), #punctuation_*
            (r'=|->|:', Operator), #operator_*
            (r'.', Text),
        ],
        'comment': [
            (r'`.*`', Literal),
            (r'@returns|@deprecated', Literal),
            (r'(@param|@throws)(\s*)(\w+)?', bygroups(Literal, Whitespace, Name.Attribute)),
            (r'\*\*[^*]+\*\*', Generic.Strong),
            (r'\*[^*]+\*', Generic.Emph),
            (r'.+?', Comment),
            (r'\n', Comment, '#pop')
        ],
        'deriving_targets': [
            (r'\w+', Name.Tag),
            (r'(\))', Punctuation, '#pop'),
        ]
    }
