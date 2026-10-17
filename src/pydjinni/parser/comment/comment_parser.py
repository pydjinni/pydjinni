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


from typing import Final

from marko import Markdown, MarkoExtension, block

from pydjinni.parser.comment.plugins import (
    DeprecatedCommand,
    InlineReference,
    ParamCommand,
    ReturnsCommand,
    ThrowsCommand,
)


class CommentParser:
    # TODO doku generator anpassen auf das neue plugin-format
    block_plugins = (
        ReturnsCommand,
        DeprecatedCommand,
        ParamCommand,
        ThrowsCommand,
    )
    inline_plugins = (InlineReference,)

    def __init__(self) -> None:
        self._markdown: Final = Markdown(
            extensions=[
                MarkoExtension(elements=list(self.block_plugins + self.inline_plugins)),
            ]
        )

    def parse(self, text: str) -> block.Document:
        return self._markdown.parse(text)
