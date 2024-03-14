from lsprotocol.types import CompletionItemKind, DiagnosticTag
from pygls.protocol import default_converter


def tolerant_converter():
    converter = default_converter()

    def completion_item_kind_hook(obj, type_):
        try:
            return CompletionItemKind(obj)
        except ValueError:
            return obj

    def diagnostic_tag_hook(obj, type_):
        try:
            return DiagnosticTag(obj)
        except ValueError:
            return obj

    converter.register_structure_hook(
        CompletionItemKind, completion_item_kind_hook
    )
    converter.register_structure_hook(
        DiagnosticTag, diagnostic_tag_hook
    )

    return converter
