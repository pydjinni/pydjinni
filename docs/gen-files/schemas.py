import mkdocs_gen_files
from pydjinni.config.config import Config
from pydjinni.parser.ast import Type

with mkdocs_gen_files.open("json-schema/config_schema.json", "w") as f:
    print(Config.__pydantic_model__.schema_json(indent=4), file=f)

with mkdocs_gen_files.open("json-schema/type_definition_schema.json", "w") as f:
    print(Type.__pydantic_model__.schema_json(indent=4), file=f)
