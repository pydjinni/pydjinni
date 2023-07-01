from pathlib import Path

from .type import ObjcExternalType

external_types: dict[str, ObjcExternalType] = {
    "bool": ObjcExternalType(typename="BOOL", boxed="NSNumber", pointer=False),
    "i8": ObjcExternalType(typename="int8_t", boxed="NSNumber", pointer=False),
    "i16": ObjcExternalType(typename="int16_t", boxed="NSNumber", pointer=False),
    "i32": ObjcExternalType(typename="int32_t", boxed="NSNumber", pointer=False),
    "i64": ObjcExternalType(typename="int64_t", boxed="NSNumber", pointer=False),
    "f32": ObjcExternalType(typename="float", boxed="NSNumber", pointer=False),
    "f64": ObjcExternalType(typename="double", boxed="NSNumber", pointer=False),
    "string": ObjcExternalType(typename="NSString", boxed="NSString"),
    "binary": ObjcExternalType(typename="NSData", boxed="NSData"),
    "date": ObjcExternalType(typename="NSDate", boxed="NSDate"),
    "list": ObjcExternalType(typename="NSArray", boxed="NSArray"),
    "set": ObjcExternalType(typename="NSSet", boxed="NSSet"),
    "map": ObjcExternalType(typename="NSDictionary", boxed="NSDictionary"),
}
