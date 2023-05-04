from mistletoe import block_token, span_token
from mistletoe.base_renderer import BaseRenderer

from pydjinni.generator.comment_renderer import BaseCommentRenderer


class DoxygenCommentRenderer(BaseCommentRenderer):

    def render_heading(self, token: block_token.Heading) -> str:
        return f"{'#' * token.level} {self.render_inner(token)}{self.NEWLINE * 2}"

    def render_list(self, token: block_token.List) -> str:
        if token.start is None:
            prefix = "-"
        else:
            prefix = "1."
        inner = ''.join([f"{prefix} {self.render(child)}" for child in token.children])
        return f"{self.NEWLINE * 2}{inner}{self.NEWLINE}"

    def render_list_item(self, token: block_token.ListItem) -> str:
        return f"{self.render_inner(token)}{self.NEWLINE}"

    def render_returns(self, token):
        return f"{self.NEWLINE}@return {self.render_inner(token)}"
