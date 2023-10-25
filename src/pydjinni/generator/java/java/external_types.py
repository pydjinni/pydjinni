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

from .type import JavaExternalType

external_types: dict[str, JavaExternalType] = {
    "bool": JavaExternalType(typename="boolean", boxed="Boolean"),
    "i8": JavaExternalType(typename='byte', boxed='Byte', reference=False),
    "i16": JavaExternalType(typename="short", boxed="Short", reference=False),
    "i32": JavaExternalType(typename="int", boxed="Integer", reference=False),
    "i64": JavaExternalType(typename="long", boxed="Long", reference=False),
    "f32": JavaExternalType(typename="float", boxed="Float", reference=False),
    "f64": JavaExternalType(typename="double", boxed="Double", reference=False),
    "string": JavaExternalType(typename="String", boxed="String", reference=False),
    "binary": JavaExternalType(typename="byte[]", boxed="byte[]"),
    "date": JavaExternalType(typename="java.time.Instant", boxed="java.time.Instant"),
    "list": JavaExternalType(typename="java.util.ArrayList", boxed="java.util.ArrayList"),
    "set": JavaExternalType(typename="java.util.HashSet", boxed="java.util.HashSet"),
    "map": JavaExternalType(typename="java.util.HashMap", boxed="java.util.HashMap"),
}
