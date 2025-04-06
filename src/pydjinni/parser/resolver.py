# Copyright 2023 jothepro
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

import copy
from pathlib import Path

import pydantic
import yaml
import re

from pydjinni.exceptions import InputParsingException, FileNotFoundException, ApplicationException
from pydjinni.parser.ast import TypeReference, BaseType
from pydjinni.parser.base_models import BaseExternalType
from pydjinni.position import Position, Cursor


class Resolver:
    class TypeResolvingException(ApplicationException, code=170):
        """Type resolving error"""

    def __init__(self, external_types_model: type[BaseExternalType]):
        self.registry = dict()
        self._external_types_model = external_types_model

    def load_external(self, path: Path):
        try:
            content = path.read_text()
            types_dict = yaml.safe_load_all(content)
            for type_dict in types_dict:
                if type_dict is not None:
                    types_type = self._external_types_model.model_validate(type_dict)
                    pattern = re.compile(r'^name: *(' + types_type.name + ')$', re.MULTILINE)
                    match = pattern.search(content)
                    if match:
                        line = content[:match.start()].count('\n') + 1
                        start = match.start(1) - content.rfind('\n', 0, match.start()) - 1
                        end = match.end(1) - content.rfind('\n', 0, match.end()) - 1
                        types_type.position = Position(file=path, start=Cursor(line=line, col=start), end=Cursor(line=line, col=end))
                    else:
                        types_type.position = Position(file=path)
                    self.register(types_type)
        except pydantic.ValidationError as e:
            raise InputParsingException.from_pydantic_error(e, file=path)
        except yaml.MarkedYAMLError as e:
            raise InputParsingException.from_yaml_error(e)
        except FileNotFoundError:
            raise FileNotFoundException(path)

    def register(self, datatype: BaseType):
        registry_name = ".".join(datatype.namespace + [datatype.name])
        if registry_name in self.registry:
            raise Resolver.TypeResolvingException(f"Type '{datatype.name}' already exists", datatype.position)
        else:
            self.registry[registry_name] = datatype

    def resolve(self, type_reference: TypeReference) -> BaseType:
        type_def: BaseType | None = None
        if type_reference.name.startswith('.'):  # absolute reference. No need to search for the type
            type_def = self.registry.get(type_reference.name[1:])
        else:  # relative type. Search in current and all above namespaces until a matching type is found
            namespace_copy = copy.deepcopy(type_reference.namespace)
            while type_def is None:
                type_def = self.registry.get('.'.join(namespace_copy + [type_reference.name]))
                if namespace_copy:
                    namespace_copy.pop()
                else:
                    break

        if type_def is None:
            raise Resolver.TypeResolvingException(
                f"Unknown type '{type_reference.name}'",
                position=type_reference.position
            )
        return type_def
