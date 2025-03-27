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

from pathlib import PurePosixPath

from .type import ObjcppExternalType

external_types: dict[str, ObjcppExternalType] = {
    "bool": ObjcppExternalType(translator="::pydjinni::translators::objc::Bool", header=PurePosixPath("pydjinni/marshal.h")),
    "i8": ObjcppExternalType(translator="::pydjinni::translators::objc::I8", header=PurePosixPath("pydjinni/marshal.h")),
    "i16": ObjcppExternalType(translator="::pydjinni::translators::objc::I16", header=PurePosixPath("pydjinni/marshal.h")),
    "i32": ObjcppExternalType(translator="::pydjinni::translators::objc::I32", header=PurePosixPath("pydjinni/marshal.h")),
    "i64": ObjcppExternalType(translator="::pydjinni::translators::objc::I64", header=PurePosixPath("pydjinni/marshal.h")),
    "f32": ObjcppExternalType(translator="::pydjinni::translators::objc::F32", header=PurePosixPath("pydjinni/marshal.h")),
    "f64": ObjcppExternalType(translator="::pydjinni::translators::objc::F64", header=PurePosixPath("pydjinni/marshal.h")),
    "string": ObjcppExternalType(translator="::pydjinni::translators::objc::String", header=PurePosixPath("pydjinni/marshal.h")),
    "binary": ObjcppExternalType(translator="::pydjinni::translators::objc::Binary", header=PurePosixPath("pydjinni/marshal.h")),
    "date": ObjcppExternalType(translator="::pydjinni::translators::objc::Date", header=PurePosixPath("pydjinni/marshal.h")),
    "list": ObjcppExternalType(translator="::pydjinni::translators::objc::List", header=PurePosixPath("pydjinni/marshal.h")),
    "set": ObjcppExternalType(translator="::pydjinni::translators::objc::Set", header=PurePosixPath("pydjinni/marshal.h")),
    "map": ObjcppExternalType(translator="::pydjinni::translators::objc::Map", header=PurePosixPath("pydjinni/marshal.h"))
}
