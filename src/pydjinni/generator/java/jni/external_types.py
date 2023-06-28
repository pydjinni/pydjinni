from pathlib import Path

from .type import JniExternalType, NativeType

external_types: dict[str, JniExternalType] = {
    "bool": JniExternalType(
        translator="::pydjinni::jni::translator::Bool",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.boolean,
        type_signature="Z"
    ),
    "i8": JniExternalType(
        translator="::pydjinni::jni::translator::I8",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.byte,
        type_signature="B"
    ),
    "i16": JniExternalType(
        translator="::pydjinni::jni::translator::I16",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.short,
        type_signature="S"
    ),
    "i32": JniExternalType(
        translator="::pydjinni::jni::translator::I32",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.int,
        type_signature="I"
    ),
    "i64": JniExternalType(
        translator="::pydjinni::jni::translator::I64",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.long,
        type_signature="J"
    ),
    "f32": JniExternalType(
        translator="::pydjinni::jni::translator::F32",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.float,
        type_signature="F"
    ),
    "f64": JniExternalType(
        translator="::pydjinni::jni::translator::F64",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.double,
        type_signature="D"
    ),
    "string": JniExternalType(
        translator="::pydjinni::jni::translator::String",
        header=Path("pydjinni/jni/marshal.hpp"),
        typename=NativeType.string,
        type_signature="Ljava/lang/String;"
    )
}
