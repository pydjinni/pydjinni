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
