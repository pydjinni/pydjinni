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
    def __init__(self, api: API, context: ContextType, clean: bool):
        super().__init__(api, context)
        self.clean = clean


class PackageConfigurationContext(Context[API.ConfiguredContext]):
    def __init__(self, api: API, context: ContextType, clean: bool, configuration: str):
        super().__init__(api, context)
        self.clean = clean
        self.configuration = configuration


class PackageContext(Context[API.ConfiguredContext.PackageContext]):
    def __init__(self, api: API, context: ContextType, clean: bool):
        super().__init__(api, context)
        self.clean = clean


pass_cli_context = click.make_pass_decorator(CliContext)
pass_generate_context = click.make_pass_decorator(GenerateContext)
pass_package_configuration_context = click.make_pass_decorator(PackageConfigurationContext)
pass_package_context = click.make_pass_decorator(PackageContext)
