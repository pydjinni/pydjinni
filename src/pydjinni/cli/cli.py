import sys
from pathlib import Path

import click

from pydjinni.api import API
from .context import CliContext, pass_cli_context, GenerateContext, pass_generate_context
from pydjinni.defs import DEFAULT_CONFIG_PATH
import logging
from rich.logging import RichHandler


class GenerateCli(click.MultiCommand):
    @classmethod
    def print_wrong_path_warning(cls):
        print('\033[31m' + "ATTENTION: This line should not appear when using the CLI!!! "
              "This code-path is only a workaround for the documentation generation!!!" + '\033[0m', file=sys.stderr)

    @click.pass_context
    def list_commands(self, ctx, generate_context: click.Context) -> list[str]:
        if generate_context.obj is None:
            logger = logging.getLogger(__name__)
            GenerateCli.print_wrong_path_warning()
            api = API(logger)
        else:
            api = generate_context.obj.api

        return list(api.generation_targets.keys())

    @click.pass_context
    def get_command(self, ctx, generate_context: click.Context, name) -> click.Command | None:
        if generate_context.obj is None:
            logger = logging.getLogger(__name__)
            GenerateCli.print_wrong_path_warning()
            api = API(logger)
        else:
            api, logger = generate_context.obj.api, generate_context.obj.logger

        target = api.generation_targets.get(name)

        @click.command(name, help=target.__doc__)
        @pass_generate_context
        def command(generate_context: GenerateContext):
            logger = generate_context.logger
            logger.info(f"Generating files for target '{name}'")
            generate_context.context.generate(name).write_out_files()
        return None if target is None else command


@click.group()
@click.version_option()
@click.pass_context
@click.option('--option', '-o', multiple=True, type=str,
              help="overwrite or extend options from the generate config. Example: `-o java.out=java_out`")
@click.option('--config', '-c', default=DEFAULT_CONFIG_PATH, type=Path,
              help="path to the config file.")
@click.option("--log-level", "-l", default="info",
              type=click.Choice(["info", "debug"]),
              help="log level")
def cli(ctx, log_level, config, option):
    logger = logging.getLogger(__name__)
    api = API(logger)
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), None),
        format="%(message)s",
        handlers=[RichHandler(show_time=False, show_path=False)]
    )
    ctx.obj = CliContext(
        api=api,
        context=api.configure(path=config, options=option),
        logger=logger
    )


@cli.command(cls=GenerateCli, chain=True, invoke_without_command=True)
@pass_cli_context
@click.pass_context
@click.argument('idl', type=Path)
def generate(ctx, cli_context: CliContext, idl: Path):
    """
    generate glue-code from the provided IDL file.

    COMMAND specifies the target languages.
    """
    logger = cli_context.logger
    logger.info("parsing idl")
    ctx.obj = GenerateContext(
        api=cli_context.api,
        context=cli_context.context.parse(idl),
        logger=logger
    )
