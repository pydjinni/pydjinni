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

from lsprotocol.types import CompletionItemKind, DiagnosticTag
from pygls.protocol import default_converter


def tolerant_converter():
    converter = default_converter()

    def completion_item_kind_hook(obj, type_):
        try:
            return CompletionItemKind(obj)
        except ValueError:
            return obj

    def diagnostic_tag_hook(obj, type_):
        try:
            return DiagnosticTag(obj)
        except ValueError:
            return obj

    converter.register_structure_hook(
        CompletionItemKind, completion_item_kind_hook
    )
    converter.register_structure_hook(
        DiagnosticTag, diagnostic_tag_hook
    )

    return converter
