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

from pydantic import create_model, BaseModel
from pydantic.fields import FieldInfo


class TypeModelBuilder:
    """
    Create the BaseModel for (external) type validation from all loaded generator modules
    """

    def __init__(self, model_base: type[BaseModel]):
        self._model_base = model_base
        self._models: dict[str, tuple[type[BaseModel], FieldInfo | None]] = {}

    def add_field(self, field_name: str, model: type[BaseModel], field_info: FieldInfo | None = None):
        self._models[field_name] = (model, field_info)

    def build(self):
        field_kwargs = {key: value for key, value in self._models.items()}
        return create_model(
            self._model_base.__name__,
            __base__=self._model_base,
            **field_kwargs
        )
