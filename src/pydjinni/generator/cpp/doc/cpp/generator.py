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

from pydjinni.documentation.generator import DocumentationGenerator
from pydjinni.parser.ast import Interface, Record, Enum, Flags


class CppDocumentation(DocumentationGenerator):
    key = "cpp"
    name = "C++"

    def generate_interface(self, decl: Interface) -> tuple[str, str]:
        return decl.cpp.name, self.template(
            "interface.jinja2",
            decl=decl
        )

    def generate_record(self, decl: Record) -> tuple[str, str]:
        return decl.cpp.name, self.template(
            "record.jinja2",
            decl=decl
        )

    def generate_enum(self, decl: Enum) -> tuple[str, str]:
        return decl.cpp.name, self.template(
            "enum.jinja2",
            decl=decl
        )

    def generate_flags(self, decl: Flags) -> tuple[str, str]:
        return decl.cpp.name, self.template(
            "flags.jinja2",
            decl=decl
        )
