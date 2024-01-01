from typing import Any

from mistune import BlockState
from mistune.renderers.markdown import MarkdownRenderer

from pydjinni.parser.ast import Interface
from pydjinni.parser.base_models import BaseCommentModel


class ParserCommentProcessor(MarkdownRenderer):
    def __init__(self, decl: BaseCommentModel):
        super().__init__()
        self.decl = decl

    def iter_tokens(self, tokens, state):
        for tok in tokens:
            try:
                yield self.render_token(tok, state)
            except AttributeError:
                pass

    def deprecated(self, token: dict[str, Any], state: BlockState) -> str:
        text = self.render_children(token, state)
        self.decl.deprecated = text if text else True
        return ""

    def param(self, token: dict[str, Any], state: BlockState):
        name = token['attrs']['name']
        description = self.render_children(token, state)
        if isinstance(self.decl, Interface.Method) and description:
            for param in self.decl.parameters:
                if param.name == name:
                    param.comment = description
                    break
        return ""
