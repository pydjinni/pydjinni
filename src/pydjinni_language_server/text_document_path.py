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

from pathlib import Path
from urllib.parse import unquote

from pygls.workspace import TextDocument


class TextDocumentPath(Path):

    def __init__(self, document: TextDocument):
        super().__init__(document.uri)
        self.document = document

    def read_text(self, encoding: str | None = None, errors: str | None = None, newline: str | None = None):
        return self.document.source

    def as_uri(self):
        return unquote(self.document.uri)
    
    def is_absolute(self) -> bool:
        return True

    @property
    def parent(self):
        return Path(self.document.path).parent
