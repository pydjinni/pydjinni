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

from .type import CppCliExternalType

external_types: dict[str, CppCliExternalType] = {
    "bool": CppCliExternalType(
        typename="bool",
        translator="::pydjinni::cppcli::translator::Bool",
        header=Path("pydjinni/cppcli/Marshal.hpp"),
        reference=False),
    "i8": CppCliExternalType(
        typename="char",
        translator="::pydjinni::cppcli::translator::I8",
        header=Path("pydjinni/cppcli/Marshal.hpp"),
        reference=False),
    "i16": CppCliExternalType(
        typename="short",
        translator="::pydjinni::cppcli::translator::I16",
        header=Path("pydjinni/cppcli/Marshal.hpp"),
        reference=False),
    "i32": CppCliExternalType(
        typename="int",
        translator="::pydjinni::cppcli::translator::I32",
        header=Path("pydjinni/cppcli/Marshal.hpp"),
        reference=False),
    "i64": CppCliExternalType(
        typename="__int64",
        translator="::pydjinni::cppcli::translator::I64",
        header=Path("pydjinni/cppcli/Marshal.hpp"),
        reference=False),
    "f32": CppCliExternalType(
        typename="float",
        translator="::pydjinni::cppcli::translator::F32",
        header=Path("pydjinni/cppcli/Marshal.hpp"),
        reference=False),
    "f64": CppCliExternalType(
        typename="double",
        translator="::pydjinni::cppcli::translator::F64",
        header=Path("pydjinni/cppcli/Marshal.hpp"),
        reference=False),
    "string": CppCliExternalType(
        typename="System::String",
        translator="::pydjinni::cppcli::translator::String",
        header=Path("pydjinni/cppcli/Marshal.hpp")),
    "binary": CppCliExternalType(
        typename="array<System::Byte>",
        translator="::pydjinni::cppcli::translator::Binary",
        header=Path("pydjinni/cppcli/Marshal.hpp")),
    "date": CppCliExternalType(
        typename="System::DateTime",
        translator="::pydjinni::cppcli::translator::Date",
        header=Path("pydjinni/cppcli/Marshal.hpp"),
        reference=False
    ),
    "list": CppCliExternalType(
        typename="System::Collections::Generic::List",
        translator="::pydjinni::cppcli::translator::List",
        header=Path("pydjinni/cppcli/Marshal.hpp")),
    "set": CppCliExternalType(
        typename="System::Collections::Generic::HashSet",
        translator="::pydjinni::cppcli::translator::Set",
        header=Path("pydjinni/cppcli/Marshal.hpp")),
    "map": CppCliExternalType(
        typename="System::Collections::Generic::Dictionary",
        translator="::pydjinni::cppcli::translator::Map",
        header=Path("pydjinni/cppcli/Marshal.hpp"))
}
