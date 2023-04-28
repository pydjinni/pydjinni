import logging
import sys
from collections import defaultdict
from pathlib import Path

import click
from rich.logging import RichHandler
from rich.pretty import pretty_repr

from pydjinni.api import API, combine_into
from pydjinni.defs import DEFAULT_CONFIG_PATH
from pydjinni.exceptions import ApplicationException
from .context import CliContext, pass_cli_context, GenerateContext, pass_generate_context

logger = logging.getLogger(__name__)


def main():
    """Entrypoint for initializing the Command Line Interface (CLI)"""
    try:
        cli(auto_envvar_prefix='PYDJINNI')
    except ApplicationException as e:
        logger.error(e)
        exit(e.code)


class GenerateCli(click.MultiCommand):
    @classmethod
    def print_wrong_path_warning(cls):
        print('\033[31m' + "ATTENTION: This line should not appear when using the CLI!!! "
                           "This code-path is only a workaround for the documentation generation!!!" + '\033[0m',
              file=sys.stderr)

    @click.pass_context
    def list_commands(self, ctx, generate_context: click.Context) -> list[str]:
        if generate_context.obj is None:
            GenerateCli.print_wrong_path_warning()
            api = API()
        else:
            api = generate_context.obj.api

        return list(api.generation_targets.keys())

    @click.pass_context
    def get_command(self, ctx, generate_context: click.Context, name) -> click.Command | None:
        if generate_context.obj is None:
            GenerateCli.print_wrong_path_warning()
            api = API()
        else:
            api = generate_context.obj.api

        target = api.generation_targets.get(name)

        @click.command(name, help=target.__doc__)
        @pass_generate_context
        def command(generate_context: GenerateContext):
            logger.info(f"Generating files for target '{name}'")
            generate_context.context.generate(name, clean=generate_context.clean).write_processed_files()

        return None if target is None else command


@click.group()
@click.version_option()
@click.pass_context
@click.option('--option', '-o', multiple=True, type=str,
              help="overwrite or extend options from the generate config. Example: `-o java.out:java_out`")
@click.option('--config', '-c', default=DEFAULT_CONFIG_PATH, type=Path,
              help="path to the config file. Set to `None` if no config should be parsed. "
                   "File format is determined based on the file extension. "
                   "Supported extensions: `.yaml`, `.yml`, `.json`, `.toml`")
@click.option("--log-level", "-l", default="info",
              type=click.Choice(["debug", "info", "warn", "error"]),
              help="log level")
def cli(ctx, log_level, config, option):
    def parse_option(option: str) -> dict:
        """
        helper to parse options in the format `foo.bar:baz` into a hierarchical dict
        Args:
            option: Option that should be parsed

        Returns:
            a dict representing the configuration hierarchy provided by the parameter

        Examples:
            >>> parse_option("foo.bar:baz")
            defaultdict(None, {'foo': {'bar': 'baz'}})
        """
        key_list, value = option.split(':', 1)
        keys = key_list.split('.')
        result = defaultdict()
        d = result
        for subkey in keys[:-1]:
            d = d.setdefault(subkey, {})
        d[keys[-1]] = value
        return result

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), None),
        format="%(message)s",
        handlers=[RichHandler(show_time=False, show_path=False)]
    )

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


@cli.command(cls=GenerateCli, chain=True, invoke_without_command=True)
@pass_cli_context
@click.pass_context
@click.option(
    '--clean',
    is_flag=True,
    help="If enabled, deletes all specified out directories before generating output. "
         "Caution: This deletes the entire folders, including all files that are inside it!")
@click.argument('idl', type=Path)
def generate(ctx, cli_context: CliContext, idl: Path, clean: bool):
    """
    generate glue-code from the provided IDL file.

    COMMAND specifies the target languages.
    """
    logger.info("parsing IDL")
    context = cli_context.context.parse(idl)
    logger.debug("Generated AST:")
    logger.debug(pretty_repr(context.ast))
    ctx.obj = GenerateContext(
        api=cli_context.api,
        context=context,
        clean=clean
    )
