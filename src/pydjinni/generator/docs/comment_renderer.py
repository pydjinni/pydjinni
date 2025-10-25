# Copyright 2025 jothepro
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


from mistune import HTMLRenderer

from pydjinni.parser.base_models import TypeReference


class DocumentationCommentRenderer(HTMLRenderer):

    def returns(self, text: str) -> str:
        return f"@return {text}\n"

    def param(self, text: str, name: str) -> str:
        return f""

    def throws(self, text: str, type_ref: TypeReference) -> str:
        return f"@throws {type_ref.name} {text}\n"

    def deprecated(self, text: str) -> str:
        return f"<p>Deprecated: {text}</p>"

