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
//? type_def.comment : type_def.cpp.comment | comment
enum class {{ type_def.cpp.deprecated ~ type_def.cpp.name }} : int {
//> for item in type_def.items:
    //? item.comment : item.cpp.comment | comment | indent
    {{ item.cpp.name ~ item.cpp.deprecated ~ ("," if not loop.last) }}
//> endfor
};
//> if config.string_serialization:
//> call disable_deprecation_warnings(type_def.deprecated)
std::string to_string({{ type_def.cpp.typename }} value) noexcept;
//> endcall
//> endif
//> endblock
//> block global
//> if config.string_serialization:
//> call disable_deprecation_warnings(type_def.deprecated)
template<>
struct std::formatter<{{ type_def.cpp.typename }}> : std::formatter<std::string> {
    template<typename FormatContext>
    auto format({{ type_def.cpp.namespace }}::{{ type_def.cpp.name }} value, FormatContext &ctx) const {
        return std::format_to(ctx.out(), "{}", {{ type_def.cpp.namespace }}::to_string(value));
    }
};
//> endcall
//> endif
//> endblock
