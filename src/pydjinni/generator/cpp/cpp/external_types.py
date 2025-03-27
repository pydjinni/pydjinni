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

from .type import CppExternalType

external_types: dict[str, CppExternalType] = {
    "bool": CppExternalType(typename="bool", by_value=True),
    "i8": CppExternalType(typename="int8_t", header=PurePosixPath("<cstdint>"), by_value=True),
    "i16": CppExternalType(typename="int16_t", header=PurePosixPath("<cstdint>"), by_value=True),
    "i32": CppExternalType(typename="int32_t", header=PurePosixPath("<cstdint>"), by_value=True),
    "i64": CppExternalType(typename="int64_t", header=PurePosixPath("<cstdint>"), by_value=True),
    "f32": CppExternalType(typename="float", by_value=True),
    "f64": CppExternalType(typename="double", by_value=True),
    "string": CppExternalType(typename="std::string", header=PurePosixPath("<string>")),
    "binary": CppExternalType(typename="std::vector<uint8_t>", header=PurePosixPath("pydjinni/type/binary.hpp")),
    "date": CppExternalType(typename="std::chrono::system_clock::time_point", header=PurePosixPath("<chrono>")),
    "list": CppExternalType(typename="std::vector", header=PurePosixPath("<vector>")),
    "set": CppExternalType(typename="std::unordered_set", header=PurePosixPath("<unordered_set>")),
    "map": CppExternalType(typename="std::unordered_map", header=PurePosixPath("<unordered_map>")),
}
