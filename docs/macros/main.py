import json
import logging
from collections import OrderedDict
from pathlib import Path
from typing import Any

from setuptools_scm import get_version

import jsonref
from mkdocs_click._docs import make_command_docs
from mkdocs_click._extension import load_command

from pydjinni.api import API
from pydjinni.exceptions import return_codes


def render_config_schema_table(element, indent: int, render_defaults=True):
    first_value = True
    result = ""
    postponed: list[tuple[str, Any]] = []
    if "properties" in element:
        for key, value in element["properties"].items():
            if value.get("allOf") and len(value["allOf"]) == 1:
                if value.get("default"):
                    value["allOf"][0]["default"] = value["default"]
                if value.get("description"):
                    value["allOf"][0]["description"] = value["description"]
                value = value["allOf"][0]
            if value.get("type") == "object":
                content = f"\n{'#' * indent} {key}\n\n"
                if value.get("description"):
                    content += f"\n{value['description'].lstrip()}\n\n"
                postponed.append((content, value))
            else:
                if first_value:
                    result += f"| Name | Type | Description |\n"
                    result += f"| ---- | ---- | ----------- |\n"
                    first_value = False
                if "title" in value and value["title"] == "Identifier":
                    result += f"| `{key}` | dict([IdentifierStyle](#identifierstyle)) |"
                elif value.get("anyOf"):
                    result += f"| `{key}` | "
                    first = True
                    for type in value["anyOf"]:
                        if first:
                            first = False
                        else:
                            result += ", "
                        if type['type'] != "object":
                            result += type['type']
                        else:
                            result += f"[{type['title']}](#{type['title'].lower()})"
                    result += " |"
                else:
                    result += f"| `{key}` | {value.get('type')} | "

                if "description" in value:
                    result += f"{value['description']}<br>"
                if "enum" in value:
                    result += f"One of `{'`, `'.join(value['enum'])}`<br>"
                if "examples" in value:
                    examples = value["examples"]
                    if len(examples) == 1:
                        result += f"**Example:** `{examples[0]}`"
                    else:
                        result += "**Examples:<br>**"
                        for example in examples:
                            result += f"- `{example}`<br>"
                if render_defaults and "default" in value and value["default"] is not None:
                    default = value['default']
                    result += "**Default:** "
                    if isinstance(default, dict):
                        result += "<br>"
                        for default_key, default_value in default.items():
                            result += f"- **{default_key}**: `{default_value}`<br>"
                    else:
                        result += f"`{value['default']}`"
                result += " |\n"
        for content, value in postponed:
            result += content
            result += render_config_schema_table(value, indent + 1, render_defaults)
    return result


def define_env(env):
    "Hook function"

    logger = logging.getLogger(__name__)
    api = API()

    @env.macro
    def idl_grammar(path: str):
        grammar = Path(path).read_text().replace(" = ", " ← ")
        return f"```peg\n{grammar}\n```\n"

    @env.macro
    def config_schema_table(header_indent: int = 3):
        json_schema = json.dumps(api.configuration_model.model_json_schema())
        schema = jsonref.loads(json_schema)
        return render_config_schema_table(schema, header_indent)

    @env.macro
    def config_schema_definition(definition: str):
        json_schema = json.dumps(api.configuration_model.model_json_schema())
        definition = jsonref.loads(json_schema)['$defs'][definition]
        return render_config_schema_table(definition, 3)

    @env.macro
    def type_schema_table(header_indent: int = 3):
        json_schema = json.dumps(api.external_type_model.model_json_schema())
        schema = jsonref.loads(json_schema)
        return render_config_schema_table(schema, header_indent)

    @env.macro
    def processed_files_schema_table(header_indent: int = 3):
        json_schema = json.dumps(api.processed_files_model.model_json_schema())
        schema = jsonref.loads(json_schema)
        return render_config_schema_table(schema, header_indent, False)

    @env.macro
    def cli_commands():
        command_obj = load_command("pydjinni.cli.cli", "cli")

        output = make_command_docs(
            prog_name="pydjinni",
            command=command_obj,
            depth=1,
            style="table",
        )
        return '\n'.join(output)

    @env.macro
    def internal_types():
        output = ""
        for type_def in api.internal_types:
            output += f"\n## {type_def.name}\n\n" \
                      f"{type_def.comment}\n\n" \
                      "| Target | Typename | Boxed |\n" \
                      "|--------|----------|-------|\n"
            for target in api.generation_targets:
                target_type = getattr(type_def, target)
                typename = f"`{target_type.typename}`"
                boxed_typename = f"`{target_type.boxed}`" if 'boxed' in target_type.model_fields_set else ''
                output += f"| {target} | {typename} | {boxed_typename} |\n"
        return output

    @env.macro
    def return_code_list():
        sorted_return_codes = OrderedDict(sorted(return_codes.items()))
        output = "| Code | Description |\n" \
                 "|------|-------------|\n"
        for code, description in sorted_return_codes.items():
            output += f"| {code} | {description} |\n"
        return output

    @env.macro
    def supported_targets(joint: str = "|", wrapper: str = ""):
        return wrapper + (wrapper + joint + wrapper).join(list(API().generation_targets.keys())) + wrapper

    @env.macro
    def pydjinni_version():
        return get_version()
