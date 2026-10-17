from typing import Any, Final
lazy from collections.abc import Sequence

from marko.block import Document
lazy from marko.element import Element

Token = dict[str, Any]


def copy_with_document(document: Document, elements: Sequence[Element]) -> Document:
    new_document: Final = Document()
    new_document.link_ref_defs = document.link_ref_defs
    new_document.children = elements
    return new_document
