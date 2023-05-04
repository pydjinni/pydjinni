from mistletoe import block_token, span_token
from mistletoe.base_renderer import BaseRenderer

from pydjinni.generator.comment_renderer import Returns, BaseCommentRenderer


class JavaDocCommentRenderer(BaseCommentRenderer):

    def render_heading(self, token: block_token.Heading) -> str:
        return f"<h{token.level}>{self.render_inner(token)}</h{token.level}>{self.NEWLINE}"

    def render_list(self, token: block_token.List) -> str:
        if token.start is None:
            tag = "ul"
        else:
            tag = "ol"
        inner = ''.join([f"{self.render(child)}" for child in token.children])
        return f"{self.NEWLINE}<{tag}>{self.NEWLINE}{inner}</{tag}>{self.NEWLINE}"

    def render_list_item(self, token: block_token.ListItem) -> str:
        return f"<li>{self.render_inner(token)}</li>{self.NEWLINE}"

    def render_returns(self, token):
        return f"{self.NEWLINE}@return {self.render_inner(token)}"
