from pathlib import Path

from pydjinni.generator.docs.generator import DocumentationGenerator
from .config import JavaDocumentationConfig
from pydjinni.parser.ast import Interface, Namespace


class JavaDocumentationGenerator(DocumentationGenerator[JavaDocumentationConfig]):
    key = "java"
    display_key = "Java"
    lexer_language = "java"

    def generate_interface(self, type_def: Interface):
        self.write_docs(Path("interface.jinja2.html"), type_def)

