from pathlib import Path

from .type import ObjcppExternalType

external_types: dict[str, ObjcppExternalType] = {
    "bool":ObjcppExternalType(
        translator="::pydjinni::translators::objc::Bool",
        header=Path("pydjinni/marshal.h")
    ),
    "i8":ObjcppExternalType(
        translator="::pydjinni::translators::objc::I8",
        header=Path("pydjinni/marshal.h")
    ),
    "i16":ObjcppExternalType(
        translator="::pydjinni::translators::objc::I16",
        header=Path("pydjinni/marshal.h")
    ),
    "i32":ObjcppExternalType(
        translator="::pydjinni::translators::objc::I32",
        header=Path("pydjinni/marshal.h")
    ),
    "i64":ObjcppExternalType(
        translator="::pydjinni::translators::objc::I64",
        header=Path("pydjinni/marshal.h")
    ),
    "f32":ObjcppExternalType(
        translator="::pydjinni::translators::objc::F32",
        header=Path("pydjinni/marshal.h")
    ),
    "f64":ObjcppExternalType(
        translator="::pydjinni::translators::objc::F64",
        header=Path("pydjinni/marshal.h")
    ),
    "string":ObjcppExternalType(
        translator="::pydjinni::translators::objc::String",
        header=Path("pydjinni/marshal.h")
    )
}
