import sys
from pathlib import Path

import click

from pydjinni.api.api import API
from .commands.init.command import init
from .commands.generate.command import generate
from .commands.package.command import package
from .commands.server.command import server
from .exceptions import ApplicationException
import logging

from rich.logging import RichHandler

logger = logging.getLogger(__name__)

logging.basicConfig(
        level="DEBUG",
        format="%(message)s",
        handlers=[RichHandler(show_time=False, show_path=False)]
    )

def main():
    try:
        cli(obj={})
    except ApplicationException as e:
        logger.error(e)
        sys.exit(e.code)


@click.group()
@click.version_option()
@click.pass_context
@click.option("--log-level", "-l", default="info",
              type=click.Choice(["info", "debug"]),
              help="log level")
def cli(ctx, log_level):
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), None),
        format="%(message)s",
        handlers=[RichHandler(show_time=False, show_path=False)]
    )
    ctx.obj = logger


cli.add_command(init)
cli.add_command(generate)
cli.add_command(package)
cli.add_command(server)


def main():
    pydjinni = API(logger)
    config = pydjinni.load_config()
    ast = pydjinni.parse(config, Path("test.djinni"))
    pydjinni.generate(pydjinni.generation_targets["cpp"], ast)
    print("foo")

if __name__ == "__main__":
    main()
