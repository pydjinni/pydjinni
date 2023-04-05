import click
from logging import Logger


pass_logger = click.make_pass_decorator(Logger)


class GenerateContext:
    def __init__(self, config, ast, interactive: bool):
        self.config = config
        self.ast = ast
        self.interactive = interactive


pass_generate_context = click.make_pass_decorator(GenerateContext)
