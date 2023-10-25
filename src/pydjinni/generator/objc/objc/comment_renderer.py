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


class DocCCommentRenderer(BaseCommentRenderer):
    def render_heading(self, token: block_token.Heading) -> str:
        return f"{'#' * token.level} {self.render_inner(token)}{self.NEWLINE * 2}"

    def render_list(self, token: block_token.List) -> str:
        if token.start is None:
            prefix = "-"
        else:
            prefix = "1."
        inner = ''.join([f"{prefix} {self.render(child)}" for child in token.children])
        return f"{self.NEWLINE * 2}{inner}{self.NEWLINE}"

    def render_list_item(self, token: block_token.ListItem) -> str:
        return f"{self.render_inner(token)}{self.NEWLINE}"

    def render_returns(self, token):
        return f"{self.NEWLINE}- Returns: {self.render_inner(token)}"
