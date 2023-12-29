# Copyright 2023 jothepro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


class PublishConfigurationContext(Context[API.ConfiguredContext]):
    def __init__(self, api: API, context: ContextType, configuration: str):
        super().__init__(api, context)
        self.configuration = configuration


class PackageContext(Context[API.ConfiguredContext.PackageContext]):
    def __init__(self, api: API, context: ContextType, clean: bool):
        super().__init__(api, context)
        self.clean = clean


pass_cli_context = click.make_pass_decorator(CliContext)
pass_generate_context = click.make_pass_decorator(GenerateContext)
pass_package_configuration_context = click.make_pass_decorator(PackageConfigurationContext)
pass_publish_configuration_context = click.make_pass_decorator(PublishConfigurationContext)
pass_package_context = click.make_pass_decorator(PackageContext)
