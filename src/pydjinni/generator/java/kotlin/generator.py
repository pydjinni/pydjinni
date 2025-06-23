# Copyright 2024 jothepro
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

from pathlib import Path
from pydjinni.generator.generator import Generator
from .type import KotlinBaseField, KotlinBaseType, KotlinExternalType, KotlinInterface
from .external_types import external_types
from pydjinni.parser.ast import Enum, Flags, Record, Interface, Function, ErrorDomain
from pydjinni.parser.base_models import BaseField, BaseType
from .config import KotlinConfig


class KotlinGenerator(Generator):
    key = "kotlin"
    config_model = KotlinConfig
    writes_source = True
    optional = True
    external_type_model = KotlinExternalType
    external_types = external_types
    marshal_models = {
        BaseType: KotlinBaseType,
        Interface: KotlinInterface,
        BaseField: KotlinBaseField,
    }

    def generate_enum(self, type_def: Enum):
        pass

    def generate_flags(self, type_def: Flags):
        pass

    def generate_record(self, type_def: Record):
        pass

    def generate_interface(self, type_def: Interface):
        self.write_source(template=Path("interface.jinja2.kt"), type_def=type_def)

    def generate_function(self, type_def: Function):
        pass

    def generate_error_domain(self, type_def: ErrorDomain):
        pass
