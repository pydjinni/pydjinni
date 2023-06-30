from pathlib import Path

from .type import CppExternalType

external_types: dict[str, CppExternalType] = {
    "bool": CppExternalType(typename="bool", by_value=True),
    "i8": CppExternalType(typename="int8_t", header=Path("<cstdint>"), by_value=True),
    "i16": CppExternalType(typename="int16_t", header=Path("<cstdint>"), by_value=True),
    "i32": CppExternalType(typename="int32_t", header=Path("<cstdint>"), by_value=True),
    "i64": CppExternalType(typename="int64_t", header=Path("<cstdint>"), by_value=True),
    "f32": CppExternalType(typename="float", by_value=True),
    "f64": CppExternalType(typename="double", by_value=True),
    "string": CppExternalType(typename="std::string", header=Path("<string>")),
    "binary": CppExternalType(typename="std::vector<uint8_t>", header=Path("<vector>")),
    "list": CppExternalType(typename="std::vector", header=Path("<vector>")),
    "set": CppExternalType(typename="std::unordered_set", header=Path("<unordered_set>")),
    "map": CppExternalType(typename="std::unordered_map", header=Path("<unordered_map>")),
}
