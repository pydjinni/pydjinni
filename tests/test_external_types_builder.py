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

from pydjinni.generator.external_types import ExternalTypesBuilder


def test_register_external_types():
    # GIVEN a specific ExternalType model
    class MyExternalType(BaseModel):
        typename: str

    # AND GIVEN an ExternalBaseType model
    class ExternalBaseType(BaseModel):
        name: str
        my: MyExternalType = None

    # AND GIVEN an ExternalTypesBuilder
    builder = ExternalTypesBuilder(external_base_type=ExternalBaseType)

    # AND GIVEN MyExternalType definitions
    external_types: dict[str, MyExternalType] = {
        "i8": MyExternalType(typename="foo"),
        "i16": MyExternalType(typename="bar")
    }

    # WHEN registering an external type
    builder.register(key="my", external_types=external_types)

    # AND WHEN building the external types
    types = builder.build()

    # THEN the types that are given as MyExternalType definitions should by available for the `my` language
    for external_type in types:
        if external_type.my:
            assert external_type.my == external_types[external_type.name]

