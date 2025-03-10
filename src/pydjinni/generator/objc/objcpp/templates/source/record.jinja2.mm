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
auto {{ type_def.objcpp.name }}::toCpp(ObjcType obj) -> CppType {
    assert(obj);
    return {
    //> for field in type_def.fields:
        //? field.deprecated : "PYDJINNI_DISABLE_DEPRECATED_WARNINGS"
        {{ field.objcpp.translator }}::toCpp(obj.{{ field.objc.name }}){{ "," if not loop.last }}
        //? field.deprecated : "PYDJINNI_ENABLE_WARNINGS"
    //> endfor
    };
}

auto {{ type_def.objcpp.name }}::fromCpp(const CppType& cpp) -> ObjcType {
    return [[::{{ type_def.objc.typename }} alloc] {{ type_def.objc.init }}
    /*>- for field in type_def.fields -*/
        {{ " " ~ field.objc.name if not loop.first }}:({{ ("PYDJINNI_DISABLE_DEPRECATED_WARNINGS" if field.deprecated ) ~ field.objcpp.translator }}::fromCpp(cpp.{{ field.cpp.name }}){{ "PYDJINNI_ENABLE_WARNINGS" if field.deprecated}})
    /*>- endfor -*/
    ];
}
//> endblock
