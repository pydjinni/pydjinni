from typing import TypeVar, Generic

import click

from pydjinni.api import API

ContextType = TypeVar("ContextType")


class Context(Generic[ContextType]):
    def __init__(self, api: API, context: ContextType):
        self.api = api
        self.context = context


class CliContext(Context[API.ConfiguredContext]):
    pass


class GenerateContext(Context[API.ConfiguredContext.GenerateContext]):
    pass


pass_cli_context = click.make_pass_decorator(CliContext)
pass_generate_context = click.make_pass_decorator(GenerateContext)
