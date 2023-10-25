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

from mistletoe import block_token

from pydjinni.generator.comment_renderer import BaseCommentRenderer


class JavaDocCommentRenderer(BaseCommentRenderer):

    def render_heading(self, token: block_token.Heading) -> str:
        return f"<h{token.level}>{self.render_inner(token)}</h{token.level}>{self.NEWLINE}"

    def render_list(self, token: block_token.List) -> str:
        if token.start is None:
            tag = "ul"
        else:
            tag = "ol"
        inner = ''.join([f"{self.render(child)}" for child in token.children])
        return f"{self.NEWLINE}<{tag}>{self.NEWLINE}{inner}</{tag}>{self.NEWLINE}"

    def render_list_item(self, token: block_token.ListItem) -> str:
        return f"<li>{self.render_inner(token)}</li>{self.NEWLINE}"

    def render_returns(self, token):
        return f"{self.NEWLINE}@return {self.render_inner(token)}"
