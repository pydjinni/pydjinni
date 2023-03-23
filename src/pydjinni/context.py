import click
from logging import Logger
from pydjinni.config.config import Config

pass_logger = click.make_pass_decorator(Logger)


class GenerateContext:
    def __init__(self, config: Config, ast, interactive: bool):
        self.config = config
        self.ast = ast
        self.interactive = interactive


pass_generate_context = click.make_pass_decorator(GenerateContext)
