import json
import logging

import mkdocs_gen_files

from pydjinni.api import API

logger = logging.getLogger(__name__)

with mkdocs_gen_files.open("json-schema/config_schema.json", "w") as f:
    print(json.dumps(API(logger).configuration_model.model_json_schema(), indent=4), file=f)

with mkdocs_gen_files.open("json-schema/type_definition_schema.json", "w") as f:
    print(json.dumps(API(logger).external_type_model.model_json_schema(), indent=4), file=f)
