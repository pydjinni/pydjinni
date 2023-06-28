from pathlib import Path

from .type import CppExternalType

external_types: dict[str, CppExternalType] = {
    "bool": CppExternalType(typename="bool"),
    "i8": CppExternalType(typename="int8_t", header=Path("<cstdint>")),
    "i16": CppExternalType(typename="int16_t", header=Path("<cstdint>")),
    "i32": CppExternalType(typename="int32_t", header=Path("<cstdint>")),
    "i64": CppExternalType(typename="int64_t", header=Path("<cstdint>")),
    "f32": CppExternalType(typename="float"),
    "f64": CppExternalType(typename="double"),
    "string": CppExternalType(typename="std::string", header=Path("<string>"))
}
