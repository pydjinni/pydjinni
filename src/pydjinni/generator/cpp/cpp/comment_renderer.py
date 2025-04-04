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
from typing import Any

from mistune import BlockState
from mistune.renderers.markdown import MarkdownRenderer

from pydjinni.generator.cpp.cpp.config import CppIdentifier
from pydjinni.parser.identifier import IdentifierType as Identifier


class DoxygenCommentRenderer(MarkdownRenderer):

    def __init__(self, identifier_style: CppIdentifier):
        super().__init__()
        self.identifier_style = identifier_style

    def returns(self, token: dict[str, Any], state: BlockState) -> str:
        return f"@returns {self.render_children(token, state)}\n"

    def param(self, token: dict[str, Any], state: BlockState) -> str:
        name = token['attrs']['name']
        return f"@param {Identifier(name).convert(self.identifier_style.field)} {self.render_children(token, state)}\n"

    def deprecated(self, token: dict[str, Any], state: BlockState) -> str:
        return f"@deprecated {self.render_children(token, state)}\n"

    def throws(self, token: dict[str, Any], state: BlockState) -> str:
        name = token['attrs']['name']
        return f"@throws {Identifier(name).convert(self.identifier_style.type)} {self.render_children(token, state)}\n"
