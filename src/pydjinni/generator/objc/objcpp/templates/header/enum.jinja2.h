/*#
Copyright 2023 jothepro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
#*/
//> extends "base.jinja2"

//> block content
struct {{ type_def.objcpp.name }} {
    using CppType = {{ type_def.cpp.typename }};
    using ObjcType = ::{{ type_def.objc.typename }};

    static CppType toCpp(ObjcType e) noexcept { return static_cast<CppType>(e); }
    static ObjcType fromCpp(CppType e) noexcept { return static_cast<ObjcType>(e); }

    struct Boxed {
        using ObjcType = NSNumber*;
        static CppType toCpp(ObjcType x) noexcept { return toCpp(x, Tag<typename std::underlying_type<CppType>::type>()); }
        static ObjcType fromCpp(CppType x) noexcept { return fromCpp(x, Tag<typename std::underlying_type<CppType>::type>()); }

    private:
        template<class T> struct Tag { };

        static CppType toCpp(ObjcType x, Tag<int>) noexcept { return {{ type_def.objcpp.translator }}::toCpp(static_cast<{{ type_def.objcpp.translator }}::ObjcType>([x integerValue])); }
        static ObjcType fromCpp(CppType x, Tag<int>) noexcept { return [NSNumber numberWithInteger:static_cast<NSInteger>({{ type_def.objcpp.translator }}::fromCpp(x))]; }

        static CppType toCpp(ObjcType x, Tag<unsigned>) noexcept { return {{ type_def.objcpp.translator }}::toCpp(static_cast<{{ type_def.objcpp.translator }}::ObjcType>([x unsignedIntegerValue])); }
        static ObjcType fromCpp(CppType x, Tag<unsigned>) noexcept { return [NSNumber numberWithUnsignedInteger:static_cast<NSUInteger>({{ type_def.objcpp.translator }}::fromCpp(x))]; }
    };
};
//> endblock
