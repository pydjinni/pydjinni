# Copyright 2024 jothepro
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
from importlib.metadata import entry_points
from pathlib import Path

import click
from rich.logging import RichHandler

from .exceptions import ApplicationException
from .templates.target import TemplateTarget

logger = logging.getLogger(__name__)


def init_plugin(plugin):
    return plugin.load()()


targets: dict[str, TemplateTarget] = {target.key: target for target in
                                      [init_plugin(plugin) for plugin in entry_points(group='pydjinni.init')]}


class TemplatesCli(click.Group):
    def list_commands(self, ctx) -> list[str]:
        return list(targets.keys())

    def get_command(self, ctx, name) -> click.Command | None:
        target = targets.get(name)

        @click.command(name, help=target.__doc__)
        @click.option(
            "--output-dir",
            type=Path,
            default=Path(),
            help="Directory where the project should be initialized"
        )
        @click.option(
            "--platforms",
            type=str,
            prompt="Target platforms",
            help="Comma separated list of system target platforms",
            default=",".join(target.supported_platforms),
            show_default=True
        )
        def command(output_dir: Path, platforms: str, **parameters):
            logger.info(f"Generating '{target.key}' template to {Path().absolute()}")
            return target.template(output_dir, platforms.split(","), parameters)
        for parameter in target.parameters:
            command = click.option(
                f'--{parameter.key}',
                type=str,
                help=parameter.description,
                default=parameter.default,
                prompt=parameter.name,
                show_default=True
            )(command)

        return None if target is None else command


def main():
    try:
        cli()
    except ApplicationException as e:
        logger.error(e)
        exit(e.code)


@click.group(cls=TemplatesCli)
@click.version_option()
@click.option(
    "--log-level", "-l",
    default="info",
    type=click.Choice(["debug", "info", "warn", "error"], case_sensitive=False),
    help="Log level"
)
def cli(log_level):
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[RichHandler(show_time=False, show_path=False, markup=True)]
    )
    logger.setLevel(log_level)
    logging.info("Welcome to the PyDjinni project wizard!")
