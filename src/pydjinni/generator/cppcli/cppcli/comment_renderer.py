# Copyright 2024 jothepro
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

from mistune import HTMLRenderer

from pydjinni.generator.cppcli.cppcli.config import CppCliIdentifierStyle
from pydjinni.parser.identifier import IdentifierType as Identifier


class XmlCommentRenderer(HTMLRenderer):

    def __init__(self, identifier_style: CppCliIdentifierStyle):
        super().__init__()
        self.identifier_style = identifier_style
        self.returns_doc = ""
        self.params_doc = []

    def heading(self, text: str, level: int, **attrs) -> str:
        match level:
            case 1:
                return f"<u><b>{text}</b></u>\n"
            case 2:
                return f"<u>{text}</u>\n"
            case 3:
                return f"<u><i>{text}</i></u>\n"
            case _:
                return text


    def paragraph(self, text: str) -> str:
        return f'<para>{text}</para>\n'

    def list(self, text: str, ordered: bool, **attrs) -> str:
        return f'<list type="{"number" if ordered else "bullet"}">\n{text}</list>\n'

    def list_item(self, text: str) -> str:
        return '<item>\n<description>' + text + '</description>\n</item>\n'

    def codespan(self, text: str) -> str:
        return f"<c>{text}</c>"

    def block_code(self, code: str, info=None) -> str:
        return f'<code>\n{code}\n</code>\n'

    def returns(self, text: str) -> str:
        self.returns_doc = f"<returns>\n{text}\n</returns>\n"
        return ""

    def param(self, text: str, name: str) -> str:
        self.params_doc.append(f'<param name="{Identifier(name).convert(self.identifier_style.local)}">{text}</param>\n')
        return ""

    def deprecated(self, text: str) -> str:
        return ""

    def render(self, tokens, state) -> str:
        summary = ''.join(self.iter_tokens(tokens, state))
        output = f"<summary>\n{summary}</summary>\n" if summary else ""
        output += ''.join(self.params_doc)
        output += self.returns_doc
        return output
