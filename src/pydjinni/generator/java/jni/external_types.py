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

from pathlib import Path

from .type import JniExternalType, NativeType

external_types: dict[str, JniExternalType] = {
    "bool": JniExternalType(
        translator="::pydjinni::jni::translator::Bool",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.boolean,
        type_signature="Z",
        boxed_type_signature="Ljava/lang/Boolean;"
    ),
    "i8": JniExternalType(
        translator="::pydjinni::jni::translator::I8",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.byte,
        type_signature="B",
        boxed_type_signature="Ljava/lang/Byte;"
    ),
    "i16": JniExternalType(
        translator="::pydjinni::jni::translator::I16",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.short,
        type_signature="S",
        boxed_type_signature="Ljava/lang/Short;"
    ),
    "i32": JniExternalType(
        translator="::pydjinni::jni::translator::I32",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.int,
        type_signature="I",
        boxed_type_signature="Ljava/lang/Integer;"
    ),
    "i64": JniExternalType(
        translator="::pydjinni::jni::translator::I64",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.long,
        type_signature="J",
        boxed_type_signature="Ljava/lang/Long;"
    ),
    "f32": JniExternalType(
        translator="::pydjinni::jni::translator::F32",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.float,
        type_signature="F",
        boxed_type_signature="Ljava/lang/Float;"
    ),
    "f64": JniExternalType(
        translator="::pydjinni::jni::translator::F64",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.double,
        type_signature="D",
        boxed_type_signature="Ljava/lang/Double;"
    ),
    "string": JniExternalType(
        translator="::pydjinni::jni::translator::String",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.string,
        type_signature="Ljava/lang/String;",
        boxed_type_signature="Ljava/lang/String;"
    ),
    "binary": JniExternalType(
        translator="::pydjinni::jni::translator::Binary",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.byte_array,
        type_signature="[B",
        boxed_type_signature="[B"
    ),
    "date": JniExternalType(
        translator="::pydjinni::jni::translator::Date",
        header=Path("pydjinni/jni/marshal.hpp"),
        type_signature="Ljava/time/Instant;",
        boxed_type_signature="Ljava/time/Instant;"
    ),
    "list": JniExternalType(
        translator="::pydjinni::jni::translator::List",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.object,
        type_signature="Ljava/util/ArrayList;",
        boxed_type_signature="Ljava/util/ArrayList;"
    ),
    "set": JniExternalType(
        translator="::pydjinni::jni::translator::Set",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.object,
        type_signature="Ljava/util/HashSet;",
        boxed_type_signature="Ljava/util/HashSet;"
    ),
    "map": JniExternalType(
        translator="::pydjinni::jni::translator::Map",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.object,
        type_signature="Ljava/util/HashMap;",
        boxed_type_signature="Ljava/util/HashMap;"
    )
}
