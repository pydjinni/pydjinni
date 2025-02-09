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

import json
from pathlib import Path

import click

from pydjinni import API
from pydjinni.defs import DEFAULT_CONFIG_PATH
from .language_server import init_language_server

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # Fallback for python < 3.11


def main():
    cli()


class ConnectionType(StrEnum):
    TCP = "TCP"
    STDIO = "STDIO"


@click.group()
@click.version_option(package_name="pydjinni")
def cli():
    """PyDjinni Language Server Utilities"""
    pass


@cli.command()
def config_schema():
    """
    Print the configuration file JSON-Schema
    """
    print(json.dumps(API().configuration_model.model_json_schema(), indent=4))


@cli.command()
@click.option('--connection',
              type=click.Choice(ConnectionType, case_sensitive=False),
              default=ConnectionType.STDIO,
              help="Connection type of the language server.")
@click.option('--host', '-h', type=str, default='127.0.0.1', help="Hostname for the TCP server.")
@click.option('--port', '-p', type=int, default=8080, help="Port for the TCP server.")
@click.option('--config', '-c', default=DEFAULT_CONFIG_PATH, type=Path, help="Path to the PyDjinni configuration file.")
@click.option('--generate-on-save', '-g', is_flag=True, help="If enabled, the generator will run on file save.")
@click.option('--generate-base-path', '-b', default=Path(), type=Path, help="Base path for the generated files.")
@click.option('--log', '-l', default=None, type=Path, help="Log file for the Language Server.")
def start(connection, host: str, port: int, config: Path, generate_on_save: bool, generate_base_path: Path, log: Path):
    """
    Start the Language Server
    """
    server = init_language_server(config=config, generate_on_save=generate_on_save, generate_base_path=generate_base_path, log=log)
    match connection:
        case ConnectionType.TCP:
            server.start_tcp(host, port)
        case ConnectionType.STDIO:
            server.start_io()
