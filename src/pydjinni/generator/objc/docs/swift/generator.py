from pathlib import Path

from pydjinni.generator.docs.generator import DocumentationGenerator
from .config import SwiftDocumentationConfig
from pydjinni.parser.ast import Interface


class SwiftDocumentationGenerator(DocumentationGenerator[SwiftDocumentationConfig]):
    key = "objc-swift"
    display_key = "Swift"
    lexer_language = "swift"

    def generate_interface(self, type_def: Interface):
        self.write_docs(Path("interface.jinja2.html"), type_def)
