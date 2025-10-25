from pathlib import Path

from pydjinni.generator.docs.generator import DocumentationGenerator
from .config import ObjcDocumentationConfig
from pydjinni.parser.ast import Interface


class ObjcDocumentationGenerator(DocumentationGenerator[ObjcDocumentationConfig]):
    key = "objc"
    display_key = "Objective-C"
    lexer_language = "objc"

    def generate_interface(self, type_def: Interface):
        self.write_docs(Path("interface.jinja2.html"), type_def)
