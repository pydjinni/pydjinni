from pathlib import Path
from pydjinni.config.config import Config
import jsonref
from mkdocs_click._docs import make_command_docs
from mkdocs_click._extension import load_command
from pydjinni.parser.ast import Type


def render_config_schema_table(element, indent: int):
    first_value = True
    result = ""
    if "properties" in element:
        for key, value in element["properties"].items():
            if value.get("type") == "object":
                result += f"\n{'#' * indent} {key}\n\n"
                result += render_config_schema_table(value, indent+1)
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
                elif value.get("allOf"):
                    for val in value["allOf"]:
                        if val.get("enum"):
                            result += f"| `{key}` | enum("

                            first = True
                            for enum_val in val["enum"]:
                                if first:
                                    first = False
                                else:
                                    result += " | "
                                result += f"`{enum_val}`"
                            result += ") |"
                else:
                    result += f"| `{key}` | {value['type']} | "

                if "description" in value:
                    result += f"{value['description']}<br>"
                if "examples" in value:
                    examples = value["examples"]
                    if len(examples) == 1:
                        result += f"**Example:** `{examples[0]}`"
                    else:
                        result += "**Examples:<br>**"
                        for example in examples:
                            result += f"- `{example}`<br>"
                if "default" in value:
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

    @env.macro
    def idl_grammar(path: str):
        grammar = Path(path).read_text().replace(" = ", " ← ")
        return f"```peg\n{grammar}\n```\n"

    @env.macro
    def config_schema_table(header_indent: int = 3):
        json_schema = Config.__pydantic_model__.schema_json()
        schema = jsonref.loads(json_schema)
        return render_config_schema_table(schema, header_indent)

    @env.macro
    def config_schema_definition(definition: str):
        json_schema = Config.__pydantic_model__.schema_json()
        definition = jsonref.loads(json_schema)['definitions'][definition]
        return render_config_schema_table(definition, 3)

    @env.macro
    def type_schema_table(header_indent: int = 3):
        json_schema = Type.__pydantic_model__.schema_json()
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

