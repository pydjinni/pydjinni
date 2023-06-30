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
    "list": JavaExternalType(typename="java.util.ArrayList", boxed="java.util.ArrayList"),
    "set": JavaExternalType(typename="java.util.HashSet", boxed="java.util.HashSet"),
    "map": JavaExternalType(typename="java.util.HashMap", boxed="java.util.HashMap"),
}
