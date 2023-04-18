import json
import mkdocs_gen_files
from pydjinni.config.config import Config
from pydjinni.parser.ast import BaseType

with mkdocs_gen_files.open("json-schema/config_schema.json", "w") as f:
    print(json.dumps(Config.model_json_schema(), indent=4), file=f)

with mkdocs_gen_files.open("json-schema/type_definition_schema.json", "w") as f:
    print(json.dumps(BaseType.model_json_schema(), indent=4), file=f)
