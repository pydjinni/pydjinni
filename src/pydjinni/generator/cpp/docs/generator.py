from pathlib import Path

from pydjinni.generator.docs.generator import DocumentationGenerator
from .config import CppDocumentationConfig
from pydjinni.parser.ast import Interface, Namespace


class CppDocumentationGenerator(DocumentationGenerator[CppDocumentationConfig]):
    key = "cpp"
    display_key = "C++"
    lexer_language = "cpp"

    def generate_interface(self, type_def: Interface):
        self.write_docs(Path("interface.jinja2.html"), type_def)


    def generate_namespace(self, type_def: Namespace):
        self.write_docs(Path("namespace.jinja2.html"), type_def)
