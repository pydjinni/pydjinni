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

from pydjinni.file.processed_files_model_builder import ProcessedFilesModelBuilder


def test_add_generated_field():
    # GIVEN a ProcessedFilesModelBuilder instance
    builder = ProcessedFilesModelBuilder()

    # WHEN adding a generated field with both header and source output enabled
    builder.add_generated_field("foo", header=True, source=True)

    # AND when building and instantiating the model
    model = builder.build()
    model_instance = model()

    # THEN the model should have the generated field
    assert "generated" in model_instance.__class__.model_fields

    # THEN the generated field should have a field for the 'foo' generator output with both header and source fields
    assert "foo" in model_instance.generated.__class__.model_fields
    assert "source" in model_instance.generated.foo.__class__.model_fields
    assert "header" in model_instance.generated.foo.__class__.model_fields


def test_add_source_only_generated_field():
    # GIVEN a ProcessedFilesModelBuilder instance
    builder = ProcessedFilesModelBuilder()

    # WHEN adding a generated field with both header and source output enabled
    builder.add_generated_field("foo", header=False, source=True)

    # AND when building and instantiating the model
    model = builder.build()
    model_instance = model()

    # THEN the model should have the generated field
    assert "generated" in model_instance.__class__.model_fields

    # THEN the generated field should have a field for the 'foo' generator output with both header and source fields
    assert "foo" in model_instance.generated.__class__.model_fields
    assert "source" in model_instance.generated.foo.__class__.model_fields
    assert "header" not in model_instance.generated.foo.__class__.model_fields
