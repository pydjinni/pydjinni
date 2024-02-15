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

from pydantic import BaseModel

from pydjinni.parser.base_models import BaseExternalType


class ExternalTypesBuilder:
    external_types: dict[str, BaseExternalType] = {
        "bool": BaseExternalType(
            name='bool',
            comment="boolean type"
        ),
        "i8": BaseExternalType(
            name='i8',
            comment="8 bit integer type"
        ),
        "i16": BaseExternalType(
            name='i16',
            comment="16 bit integer type"
        ),
        "i32": BaseExternalType(
            name='i32',
            comment="32 bit integer type"
        ),
        "i64": BaseExternalType(
            name='i64',
            comment="64 bit integer type"
        ),
        "f32": BaseExternalType(
            name='f32',
            comment="float type"
        ),
        "f64": BaseExternalType(
            name='f64',
            comment="double type"
        ),
        "string": BaseExternalType(
            name='string',
            comment="UTF-8 string type"
        ),
        "binary": BaseExternalType(
            name='binary',
            comment="binary data"
        ),
        "date": BaseExternalType(
            name='date',
            comment="point in time without timezone information in millisecond precision"
        ),
        "list": BaseExternalType(
            name='list',
            comment="a list of items of type T",
            params=["T"],
            primitive=BaseExternalType.Primitive.collection

        ),
        "set": BaseExternalType(
            name='set',
            comment="a set of unique items of type T",
            params=["T"],
            primitive=BaseExternalType.Primitive.collection

        ),
        "map": BaseExternalType(
            name='map',
            comment="a map of key-value pairs of type K, V",
            params=["K", "V"],
            primitive=BaseExternalType.Primitive.collection
        )
    }

    def __init__(self, external_base_type: type[BaseModel]):
        self._external_base_type = external_base_type
        self._external_types: dict[str, dict] = {}

    def register(self, key: str, external_types: dict):
        self._external_types[key] = external_types

    def build(self) -> list:
        output = []
        for field, model in self.external_types.items():
            field_kwargs = {key: external_types[field] for key, external_types in self._external_types.items() if
                            external_types.get(field)}
            output.append(self._external_base_type(
                name=model.name,
                primitive=model.primitive,
                comment=model.comment,
                params=model.params,
                **field_kwargs
            ))
        return output
