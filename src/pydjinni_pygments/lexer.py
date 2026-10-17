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

from pygments.lexer import (
    RegexLexer,
    bygroups,  # pyright: ignore[reportUnknownVariableType]
    words,
)
from pygments.token import Token


class PyDjinniLexer(RegexLexer):
    name = "PyDjinni"
    aliases = ("pydjinni", "djinni")
    filenames = ("*.pydjinni", "*.djinni")

    tokens = {  # noqa: RUF012
        "root": [
            (r"#", Token.Comment, "comment"),  # comment
            (r"@import|@extern", Token.Keyword.Reserved),  # import
            (r'".*"', Token.String.Double),  # string
            (r"(?<=\=)(\s*)(all|none)", bygroups(Token.Whitespace, Token.Name.Builtin)),  # enum_modifiers
            (
                words(
                    ("interface", "enum", "record", "flags", "error", "function", "namespace"),
                    prefix=r"\b",
                    suffix=r"\b",
                ),
                Token.Keyword.Type,
            ),  # types
            (
                words(
                    ("const", "static", "async", "throws", "main", "readonly", "host", "native", "shared"),
                    prefix=r"\b",
                    suffix=r"\b",
                ),
                Token.Keyword.Reserved,
            ),  # modifiers
            (
                r"\b(deriving)(\s*)(\()",
                bygroups(Token.Keyword.Reserved, Token.Whitespace, Token.Punctuation),
                "deriving_targets",
            ),  # deriving_targets
            (r"([\w]+)(\s*)(?=\=)", bygroups(Token.Name.Class, Token.Whitespace)),  # typename
            (r"(?<=:)(\s*)([<>\w]+)", bygroups(Token.Whitespace, Token.Name.Class)),  # typename_reference_parameter
            (r"(?<=->)(\s*)([<>\w]+)", bygroups(Token.Whitespace, Token.Name.Class)),  # typename_reference_return
            (r"(?<=\.)([<>\w]+)", Token.Name.Class),  # typename_reference_namespace
            (
                r"(?<=throws)(\s*)([<>\w]+)(\s*)(?=,|.)",
                bygroups(Token.Whitespace, Token.Name.Class, Token.Whitespace),
            ),  # typename_reference_throws_1
            (
                r"(?<=throws)(\s*)([<>\w]+)(\s*)(?=->)",
                bygroups(Token.Whitespace, Token.Name.Class, Token.Whitespace),
            ),  # typename_reference_throws_2
            (
                r"(?<=throws)(\s*)([<>\w]+)(\s*)(?=;)",
                bygroups(Token.Whitespace, Token.Name.Class, Token.Whitespace),
            ),  # typename_reference_throws_3
            (
                r"(?<=,)(\s*)([<>\w]+)(\s*)(?=,|.)",
                bygroups(Token.Whitespace, Token.Name.Class, Token.Whitespace),
            ),  # typename_reference_throws_4
            (
                r"(?<=,)(\s*)([<>\w]+)(\s*)(?=->)",
                bygroups(Token.Whitespace, Token.Name.Class, Token.Whitespace),
            ),  # typename_reference_throws_5
            (
                r"(?<=,)(\s*)([<>\w]+)(\s*)(?=;)",
                bygroups(Token.Whitespace, Token.Name.Class, Token.Whitespace),
            ),  # typename_reference_throws_6
            (r"(?<=namespace)(\s*)([\w]+)", bygroups(Token.Whitespace, Token.Name.Namespace)),  # namespace_typename
            (r"([\w]+)(\s*)(?=:|\(|=\s*all|=\s*none|;)", bygroups(Token.Name, Token.Whitespace)),  # parameter
            (r"([+-][\w]+)", Token.Name.Tag),  # interface_targets
            (r";|{|}|,|\.|\(|\)|<|>|\?", Token.Punctuation),  # punctuation_*
            (r"=|->|:", Token.Operator),  # operator_*
            (r".", Token.Text),
        ],
        "comment": [
            (r"`.*`", Token.Literal),
            (r"@returns|@deprecated", Token.Literal),
            (r"(@param)(\s*)(\w+)?", bygroups(Token.Literal, Token.Whitespace, Token.Name.Attribute)),
            (r"(@throws)(\s*)([\w.]+)?", bygroups(Token.Literal, Token.Whitespace, Token.Name.Attribute)),
            (r"\*\*[^*]+\*\*", Token.Generic.Strong),
            (r"\*[^*]+\*", Token.Generic.Emph),
            (r".+?", Token.Comment),
            (r"\n", Token.Comment, "#pop"),
        ],
        "deriving_targets": [
            (r"\w+", Token.Name.Tag),
            (r"(\))", Token.Punctuation, "#pop"),
        ],
    }
