import json
import mkdocs_gen_files
from pydjinni.config.config import Config
from pydjinni.parser.ast import Type

with mkdocs_gen_files.open("json-schema/config_schema.json", "w") as f:
    print(json.dumps(Config.model_json_schema(), indent=4), file=f)

with mkdocs_gen_files.open("json-schema/type_definition_schema.json", "w") as f:
    print(json.dumps(Type.model_json_schema(), indent=4), file=f)
