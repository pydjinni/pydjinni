from pathlib import Path

from pydjinni.generator.docs.generator import DocumentationGenerator
from .config import CsharpDocumentationConfig
from pydjinni.parser.ast import Interface, Namespace


class CsharpDocumentationGenerator(DocumentationGenerator[CsharpDocumentationConfig]):
    key = "csharp"
    display_key = "C#"
    lexer_language = "csharp"

    def generate_interface(self, type_def: Interface):
        self.write_docs(Path("interface.jinja2.html"), type_def)


