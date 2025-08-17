from .type import KotlinExternalType

external_types: dict[str, KotlinExternalType] = {
    "bool": KotlinExternalType(typename="kotlin.Boolean"),
    "i8": KotlinExternalType(typename='kotlin.Byte'),
    "i16": KotlinExternalType(typename="kotlin.Short"),
    "i32": KotlinExternalType(typename="kotlin.Int"),
    "i64": KotlinExternalType(typename="kotlin.Long"),
    "f32": KotlinExternalType(typename="kotlin.Float"),
    "f64": KotlinExternalType(typename="kotlin.Double"),
    "string": KotlinExternalType(typename="kotlin.String"),
    "binary": KotlinExternalType(typename="kotlin.ByteArray"),
    "date": KotlinExternalType(typename="java.time.Instant"),
    "list": KotlinExternalType(typename="java.util.ArrayList"),
    "set": KotlinExternalType(typename="java.util.HashSet"),
    "map": KotlinExternalType(typename="java.util.HashMap"),
}
