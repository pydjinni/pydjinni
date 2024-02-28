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

import logging
import sys
from collections import defaultdict
from pathlib import Path

import click
from rich.logging import RichHandler
from rich.pretty import pretty_repr

from pydjinni.api import API, combine_into
from pydjinni.defs import DEFAULT_CONFIG_PATH
from pydjinni.exceptions import ApplicationException, ApplicationExceptionList
from .context import (
    CliContext, pass_cli_context,
    GenerateContext, pass_generate_context,
    PackageContext, pass_package_context,
    PackageConfigurationContext, pass_package_configuration_context,
    PublishConfigurationContext, pass_publish_configuration_context
)
from pydjinni.packaging.architecture import Architecture

logger = logging.getLogger(__name__)


def main():
    """Entrypoint for initializing the Command Line Interface (CLI)"""
    try:
        cli()
    except ApplicationException as e:
        logger.error(e)
        exit(e.code)
    except ApplicationExceptionList as e:
        for item in e.items:
            logger.error(item)
        exit(e.items[0].code)


class MultiCommand(click.Group):
    @staticmethod
    def get_api(context: click.Context):
        if context.obj is None:
            print('\033[31m' + "ATTENTION: This line should not appear when using the CLI!!! "
                               "This code-path is only a workaround for the documentation generation!!!" + '\033[0m',
                  file=sys.stderr)
            return API()
        else:
            return context.obj.api


class GenerateCli(MultiCommand):
    @click.pass_context
    def list_commands(self, ctx, generate_context: click.Context) -> list[str]:
        api = MultiCommand.get_api(generate_context)
        return list(api.generation_targets.keys())

    @click.pass_context
    def get_command(self, ctx, generate_context: click.Context, name) -> click.Command | None:
        api = MultiCommand.get_api(generate_context)
        target = api.generation_targets.get(name)

        @click.command(name, help=target.__doc__)
        @pass_generate_context
        def command(generate_context: GenerateContext):
            logger.info(f"generating files for target '{name}'")
            return generate_context.context.generate(name, clean=generate_context.clean)

        return None if target is None else command


class PackageCli(MultiCommand):

    @click.pass_context
    def list_commands(self, ctx, package_configuration_context: click.Context) -> list[str]:
        api = MultiCommand.get_api(package_configuration_context)

        output = list(api.package_targets.keys())
        return output

    @click.pass_context
    def get_command(self, ctx, context: click.Context, name) -> click.Command | None:
        api = MultiCommand.get_api(context)
        target = api.package_targets.get(name)

        @click.group(name, cls=BuildCli, chain=True, help=target.__doc__)
        @pass_package_configuration_context
        @click.pass_context
        def command(ctx, package_configuration_context: PackageConfigurationContext):
            logger.info(f"packaging for '{name}'")
            context = package_configuration_context.context.package(name,
                                                                    configuration=package_configuration_context.configuration)
            ctx.obj = PackageContext(
                api=api,
                context=context,
                clean=package_configuration_context.clean
            )

        return None if target is None else command


class BuildCli(MultiCommand):
    @click.pass_context
    def list_commands(self, ctx, package_context: click.Context) -> list[str]:
        api = MultiCommand.get_api(package_context)
        return list(api.package_targets[ctx.name].platforms.keys())

    @click.pass_context
    def get_command(self, ctx, package_context: click.Context, name) -> click.Command | None:
        api = MultiCommand.get_api(package_context)
        target_architectures = api.package_targets[ctx.name].platforms.get(name)

        @click.command(name)
        @pass_package_context
        @click.option("--arch", multiple=True, type=click.Choice(target_architectures),
                      help="Architectures that the library should be built for. "
                           "Overrides the defaults configured in the configuration file.")
        def command(package_context: PackageContext, arch: list[Architecture]):
            logger.info(f"building for '{name}'")
            return package_context.context.build(name, architectures=set(arch), clean=package_context.clean)

        return None if target_architectures is None else command


class PublishCli(MultiCommand):
    @click.pass_context
    def list_commands(self, ctx, context: click.Context) -> list[str]:
        api = MultiCommand.get_api(context)
        return list(api.package_targets.keys())

    @click.pass_context
    def get_command(self, ctx, context: click.Context, name) -> click.Command | None:
        api = MultiCommand.get_api(context)
        target = api.package_targets.get(name)

        @click.command(name, help=target.__doc__)
        @pass_publish_configuration_context
        def command(publish_configuration_context: PublishConfigurationContext):
            logger.info(f"publishing '{name}'")
            publish_configuration_context.context.publish(
                name,
                configuration=publish_configuration_context.configuration
            )

        return None if target is None else command


@click.group()
@click.version_option()
@click.pass_context
@click.option('--option', '-o', multiple=True, type=str,
              help="Overwrite or extend configuration. Example: `-o generate.java.out=java_out`")
@click.option('--config', '-c', default=DEFAULT_CONFIG_PATH, type=Path,
              help="Path to the config file. Set to `None` if no config should be parsed. "
                   "File format is determined based on the file extension. "
                   "Supported extensions: `.yaml`, `.yml`, `.json`, `.toml`")
@click.option("--log-level", "-l", default="info",
              type=click.Choice(["debug", "info", "warn", "error"], case_sensitive=False),
              help="Log level")
def cli(ctx, log_level, config, option):
    def parse_option(option: str) -> dict:
        """
        helper to parse options in the format `foo.bar=baz` into a hierarchical dict
        Args:
            option: Option that should be parsed

        Returns:
            a dict representing the configuration hierarchy provided by the parameter

        Examples:
            >>> parse_option("foo.bar=baz")
            defaultdict(None, {'foo': {'bar': 'baz'}})
        """
        key_list, value = option.split('=', 1)
        keys = key_list.split('.')
        result = defaultdict()
        d = result
        for subkey in keys[:-1]:
            d = d.setdefault(subkey, {})
        d[keys[-1]] = value
        return result

    log_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[RichHandler(show_time=False, show_path=False, markup=True)]
    )
    logger.setLevel(log_level)

    options_dict = dict()
    for value in option:
        combine_into(parse_option(value), options_dict)
    if config in [Path("None"), Path("none"), Path("False"), Path("false")]:
        config = None

    api = API()
    context = api.configure(path=config, options=options_dict)
    logger.debug("Configuration:")
    logger.debug(pretty_repr(context.config))
    ctx.obj = CliContext(
        api=api,
        context=context
    )


@cli.group(cls=GenerateCli, chain=True)
@pass_cli_context
@click.pass_context
@click.option(
    '--clean',
    is_flag=True,
    help="If enabled, deletes all specified output directories before generating new output. "
         "Caution: This deletes the entire output folders, including all files that are inside it!")
@click.argument('idl', type=Path)
def generate(ctx, cli_context: CliContext, idl: Path, clean: bool):
    """
    Generate glue-code from the provided IDL file.

    COMMAND specifies the target languages.
    """
    logger.info("parsing IDL")
    context = cli_context.context.parse(idl)
    logger.debug("generated AST:")
    if logger.level <= logging.DEBUG:
        logger.debug(pretty_repr(context.ast))
    ctx.obj = GenerateContext(
        api=cli_context.api,
        context=context,
        clean=clean
    )


@generate.result_callback()
def generate_callback(generate_context, idl, clean):
    output = generate_context[0].write_processed_files()
    if output:
        logger.info(f"report available at: {output.absolute()}")


@cli.group(cls=PackageCli)
@pass_cli_context
@click.pass_context
@click.option("--configuration", type=str,
              help="The build configuration of the resulting package and all contained binaries")
@click.option(
    '--clean',
    is_flag=True,
    help="If enabled, deletes all used build directories before building new output. "
         "Caution: This deletes the entire folders, including all files that are inside it!")
def package(ctx, cli_context: CliContext, clean: bool, configuration: str):
    """
    Bundle an artifact for distribution.
    """
    ctx.obj = PackageConfigurationContext(
        api=cli_context.api,
        context=cli_context.context,
        configuration=configuration,
        clean=clean
    )


@package.result_callback()
def package_callback(package_context, clean: bool, configuration: str):
    logger.info("bundling package")
    output = package_context[0].write_package(clean=clean)
    logger.info(f"final distributable package: {output.absolute()}")


@cli.group(cls=PublishCli)
@pass_cli_context
@click.pass_context
@click.option("--configuration", type=str,
              help="The build configuration that should be published")
def publish(ctx, cli_context: CliContext, configuration: str):
    """
    Publish an artifact to a registry/repository.
    """
    ctx.obj = PublishConfigurationContext(
        api=cli_context.api,
        context=cli_context.context,
        configuration=configuration
    )
