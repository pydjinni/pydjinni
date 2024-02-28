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
