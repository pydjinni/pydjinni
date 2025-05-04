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
from .server import server
from enum import StrEnum


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
@click.option(
    "--connection",
    type=click.Choice(ConnectionType, case_sensitive=False),
    default=ConnectionType.STDIO,
    help="Connection type of the language server.",
)
@click.option("--host", "-h", type=str, default="127.0.0.1", help="Hostname for the TCP server.")
@click.option("--port", "-p", type=int, default=8080, help="Port for the TCP server.")
def start(connection, host: str, port: int):
    """
    Start the Language Server
    """
    match connection:
        case ConnectionType.TCP:
            server.start_tcp(host, port)
        case ConnectionType.STDIO:
            server.start_io()
