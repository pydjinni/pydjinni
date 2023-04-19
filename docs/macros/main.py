import json
import logging
from pathlib import Path
import jsonref
from mkdocs_click._docs import make_command_docs
from mkdocs_click._extension import load_command

from pydjinni.api import API


def render_config_schema_table(element, indent: int):
    first_value = True
    result = ""
    if "properties" in element:
        for key, value in element["properties"].items():
            if value.get("allOf") and len(value["allOf"]) == 1:
                value = value["allOf"][0]
            if value.get("type") == "object":
                result += f"\n{'#' * indent} {key}\n\n"
                if value.get("description"):
                    result += f"\n{value['description']}\n\n"
                result += render_config_schema_table(value, indent + 1)
            if value.get("type") != "object":
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
                    result += f"one of `{'`, `'.join(value['enum'])}`<br>"
                if "examples" in value:
                    examples = value["examples"]
                    if len(examples) == 1:
                        result += f"**Example:** `{examples[0]}`"
                    else:
                        result += "**Examples:<br>**"
                        for example in examples:
                            result += f"- `{example}`<br>"
                if "default" in value and value["default"] is not None:
                    default = value['default']
                    result += "**Default:** "
                    if isinstance(default, dict):
                        result += "<br>"
                        for default_key, default_value in default.items():
                            result += f"- **{default_key}**: `{default_value}`<br>"
                    else:
                        result += f"`{value['default']}`"
                result += " |\n"

    return result


def define_env(env):
    "Hook function"

    logger = logging.getLogger(__name__)
    api = API(logger)

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
    def cli_commands():
        command_obj = load_command("pydjinni.__main__", "cli")

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
            output += f"\n## {type_def.name}\n"
            output += "| Target | Typename | Boxed |\n"
            output += "|--------|----------|-------|\n"
            for target in api.generation_targets:
                target_type = getattr(type_def, target)
                typename = f"`{target_type.typename}`"
                boxed_typename = f"`{target_type.boxed}`" if 'boxed' in target_type.model_fields_set else ''
                output += f"| {target} | {typename} | {boxed_typename} |\n"
        return output
