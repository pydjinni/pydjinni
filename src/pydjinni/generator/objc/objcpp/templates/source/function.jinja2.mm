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
    if(obj) {
        return [obj](
            /*>- for parameter in type_def.parameters -*/
                {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last)  }}
            /*>- endfor -*/
        ){
            //> if not type_def.cpp.noexcept:
            NSError* error;
            //> endif
            {{ "auto result = " if type_def.return_type_ref }}obj(
                //>- for parameter in type_def.parameters:
                {{ parameter.objcpp.translator }}::fromCpp({{ parameter.cpp.name }}){{ ", " if not loop.last }}
                //>- endfor
                //? not type_def.cpp.noexcept : (", " if type_def.parameters) ~ "&error"
            );
            {{ objc_error_handling(type_def) | indent(8) }}
            //> if type_def.return_type_ref:
            return {{ type_def.objcpp.return_type_translator }}::toCpp(result);
            //> endif
        };
    } else return nullptr;
}

auto {{ type_def.objcpp.name }}::fromCppOpt(CppOptType cpp) -> ObjcType {
    if(cpp) {
        return ^ (
            /*>- for parameter in type_def.parameters -*/
                {{ parameter.objc.type_decl }} {{ parameter.objc.name ~ (", " if not loop.last)  }}
            /*>- endfor -*/
            /*>- if not type_def.cpp.noexcept -*/
            {{ ", " if type_def.parameters}}NSError** error
            /*>- endif -*/
        ) {
            //> call cpp_error_handling(type_def)
            {{ "auto result = " if type_def.return_type_ref }}cpp(
                //> for parameter in type_def.parameters:
                {{ parameter.objcpp.translator }}::toCpp({{ parameter.objc.name }}){{ ", " if not loop.last }}
                //> endfor
            );
            //> if type_def.return_type_ref
            return {{ type_def.objcpp.return_type_translator }}::fromCpp(result);
            //> endif
            //> endcall
        };
    } else return nil;
}

auto {{ type_def.objcpp.name }}::fromCpp(CppType cpp) -> ObjcType { return fromCppOpt(cpp); }
//> endblock
