import yaml

from pydjinni.config.config_factory import ConfigFactory
from pydjinni.exceptions import ParsingException
from pathlib import Path
from logging import Logger
import pydantic
from collections import defaultdict

from pydjinni.generator.cpp import cpp_target
from pydjinni.generator.java import java_target
from pydjinni.generator.objc import objc_target
from rich.pretty import pretty_repr

def _parse_option(option: str, option_group: str) -> dict:
    key_list, value = option.split('=', 1)
    keys = key_list.split('.')
    keys.insert(0, option_group)
    result = defaultdict()
    d = result
    for subkey in keys[:-1]:
        d = d.setdefault(subkey, {})
    d[keys[-1]] = value
    return result

def _combine_into(d: dict, combined: dict) -> None:
    for k, v in d.items():
        if isinstance(v, dict):
            _combine_into(v, combined.setdefault(k, {}))
        else:
            combined[k] = v


Config = ConfigFactory()\
        .add_target(cpp_target)\
        .add_target(java_target)\
        .add_target(objc_target)\
        .build()

def load_config(path: Path, options: tuple[str], option_group: str, logger: Logger) -> Config:
    try:
        logger.debug("Loading configuration")
        config_dict = yaml.safe_load(path.read_text())
        for option in options:
            _combine_into(_parse_option(option, option_group), config_dict)
        logger.debug(pretty_repr(config_dict))
        config = Config.parse_obj(config_dict)
        logger.debug(pretty_repr(config))
        return config
    except pydantic.ValidationError as e:
        raise ParsingException(e)
