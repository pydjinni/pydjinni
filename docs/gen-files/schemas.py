import json

import mkdocs_gen_files

from pydjinni.api import API

with mkdocs_gen_files.open("json-schema/config_schema.json", "w") as f:
    print(json.dumps(API().configuration_model.model_json_schema(), indent=4), file=f)

with mkdocs_gen_files.open("json-schema/type_definition_schema.json", "w") as f:
    print(json.dumps(API().external_type_model.model_json_schema(), indent=4), file=f)

with mkdocs_gen_files.open("json-schema/processed_files_definition_schema.json", "w") as f:
    print(json.dumps(API().processed_files_model.model_json_schema(), indent=4), file=f)
