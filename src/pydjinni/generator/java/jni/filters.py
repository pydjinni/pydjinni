from pydjinni.generator.java.jni.type import NativeType


def get_field_accessor(native_type: NativeType) -> str:
    return f"Get{native_type[1:].capitalize()}Field"
