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

import re

from mistletoe import span_token, block_token
from mistletoe.base_renderer import BaseRenderer
from mistletoe.block_token import BlockToken


class BaseCommentRenderer(BaseRenderer):
    def __init__(self):
        super().__init__(Returns)

    NEWLINE = "\n * "

    def render_line_break(self, token: span_token.LineBreak) -> str:
        return self.NEWLINE

    def render_document(self, token: block_token.Document) -> str:
        inner = self.render_inner(token)
        if len(inner.split('\n')) == 1:
            return f"/** {self.render_inner(token)} */"
        else:
            return f"/**\n * {self.render_inner(token)}\n */"

    def render_paragraph(self, token: block_token.Paragraph) -> str:
        return f"{self.render_inner(token)}"


class Returns(BlockToken):
    pattern = re.compile(r' *@return[s]? (.*)')
    content = ''

    def __init__(self, match):
        content = ' '.join([self.pattern.match(match[0]).group(1)] + match[1:])
        super().__init__(content, span_token.tokenize_inner)

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line) is not None
