# Copyright 2025 jothepro
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

from pydjinni.parser.base_models import TypeReference


class HoverTooltipCommentRenderer(MarkdownRenderer):
    def returns(self, token: dict[str, Any], state: BlockState) -> str:
        return f"\n**Returns** {self.render_children(token, state)}\n"

    def param(self, token: dict[str, Any], state: BlockState) -> str:
        name = token['attrs']['name']
        return f"\n**Parameter** `{name}` {self.render_children(token, state)}\n"

    def deprecated(self, token: dict[str, Any], state: BlockState) -> str:
        return f"\n**Deprecated** {self.render_children(token, state)}\n"

    def throws(self, token: dict[str, Any], state: BlockState) -> str:
        type_ref: TypeReference = token['attrs']['type_ref']
        return f"\n**Throws** `{type_ref.name}` {self.render_children(token, state)}\n"
