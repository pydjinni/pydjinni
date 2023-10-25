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

from pydjinni.parser.type_model_builder import TypeModelBuilder


def test_add_field():
    # GIVEN a base type model
    class BaseTypeModel(BaseModel, extra="allow"):
        foo: int = 1

    # AND GIVEN a TypeModelFactory
    builder = TypeModelBuilder(BaseTypeModel)

    # AND GIVEN a Field type model
    class FieldTypeModel(BaseModel):
        bar: int = 2

    # WHEN adding the field
    builder.add_field("name", FieldTypeModel)

    # AND WHEN building the model
    type_model = builder.build()

    # THEN the model should contain the field
    assert "name" in type_model.model_fields
    assert type_model.model_fields["name"].annotation == FieldTypeModel
