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


from mistune import HTMLRenderer
from mistune.util import escape as escape_text

from pydjinni.generator.java.java.config import JavaIdentifierStyle
from pydjinni.parser.identifier import IdentifierType as Identifier


class JavaDocCommentRenderer(HTMLRenderer):

    def __init__(self, identifier_style: JavaIdentifierStyle):
        super().__init__()
        self.identifier_style = identifier_style

    def paragraph(self, text: str) -> str:
        return f'{text}\n\n'

    def codespan(self, text: str) -> str:
        return f'{{@code {text}}}'

    def block_code(self, code: str, info=None) -> str:
        return f'<pre>{{@code{escape_text(code)}}}</pre>\n'

    def returns(self, text: str) -> str:
        return f"@return {text}\n"

    def param(self, text: str, name: str) -> str:
        return f"@param {Identifier(name).convert(self.identifier_style.field)} {text}\n"

    def deprecated(self, text: str) -> str:
        return f"@deprecated {text}\n"
