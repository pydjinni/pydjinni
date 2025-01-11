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
    return [obj](
        /*>- for parameter in type_def.parameters -*/
            {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last)  }}
        /*>- endfor -*/
    ){
        {{ "auto result = " if type_def.return_type_ref }}obj(
            //> for parameter in type_def.parameters:
            {{ parameter.type_ref | translator }}::fromCpp({{ parameter.cpp.name }}){{ ", " if not loop.last }}
            //> endfor
        );
        //> if type_def.return_type_ref:
        return {{ type_def.return_type_ref | translator }}::toCpp(result);
        //> endif
    };
}

auto {{ type_def.objcpp.name }}::fromCpp(CppType cpp) -> ObjcType {
    return ^ (
        /*>- for parameter in type_def.parameters -*/
            {{ parameter.objc.type_decl }} {{ parameter.objc.name ~ (", " if not loop.last)  }}
        /*>- endfor -*/
    ) {
        try {
            {{ "auto result = " if type_def.return_type_ref }}cpp(
                //> for parameter in type_def.parameters:
                {{ parameter.type_ref | translator }}::toCpp({{ parameter.objc.name }}){{ ", " if not loop.last }}
                //> endfor
            );
            //> if type_def.return_type_ref
            return {{ type_def.return_type_ref | translator }}::fromCpp(result);
            //> endif
        } DJINNI_TRANSLATE_EXCEPTIONS()
    };
}
//> endblock
