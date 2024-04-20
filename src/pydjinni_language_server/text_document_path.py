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

import os
import sys
from pathlib import Path, WindowsPath, PosixPath

from pygls.workspace import TextDocument

if sys.version_info >= (3, 12):
    class TextDocumentPath(Path):

        def __init__(self, document: TextDocument):
            super().__init__(document.uri)
            self.document = document

        def read_text(self, encoding=None, errors=None):
            return self.document.source

        def as_uri(self):
            return self.document.uri

else:
    class TextDocumentPath(WindowsPath if os.name == 'nt' else PosixPath):
        def __new__(cls, document: TextDocument):
            self = super().__new__(cls, document.uri)
            self.document = document
            return self

        def read_text(self, encoding=None, errors=None):
            return self.document.source

        def as_uri(self):
            return self.document.uri
