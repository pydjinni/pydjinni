/*#
Copyright 2023 -2024 jothepro

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
//> if config.string_serialization:
//> call disable_deprecation_warnings(type_def.deprecated)
std::string to_string({{ type_def.cpp.typename }} value) noexcept {
    std::string output;
    std::string separator = " | ";
    //> for flag in type_def.flags if not (flag.all or flag.none):
    //> call disable_deprecation_warnings(flag.deprecated and not type_def.deprecated)
    if((bool)(value & {{ type_def.cpp.typename }}::{{ flag.cpp.name }})) {
        if(!output.empty()) output += separator;
        output += "{{ flag.cpp.name }}";
    }
    //> endcall
    //> endfor
    return output;
}
//> endcall
//> endif
//> endblock
