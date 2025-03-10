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
//> if type_def.cpp.base_type:
struct {{ type_def.cpp.derived_name }};
//> endif
//? type_def.comment : type_def.cpp.comment | comment
struct {{ type_def.cpp.deprecated ~ type_def.cpp.name }}{{ " final" if not type_def.cpp.base_type }} {
    //> for field in type_def.fields:
    //? field.comment :  field.cpp.comment | comment | indent
    const {{ field.cpp.type_spec }} {{ field.cpp.name ~ field.cpp.deprecated }};
    //> endfor
    //? type_def.cpp.constructor_comment : type_def.cpp.constructor_comment | comment | indent
    //> call disable_deprecation_warnings(type_def.deprecated or (type_def.fields | map(attribute='deprecated') | any))
    {{ type_def.cpp.name }}(
    /*>- for field in type_def.fields -*/
        {{ field.cpp.type_spec }} {{ field.cpp.name ~ (", " if not loop.last) }}
    /*>- endfor */)
    //> for field in type_def.fields:
    {{ (": " if loop.first else ', ') ~ field.cpp.name }}(std::move({{ field.cpp.name }}))
    //> endfor
    {}
    //> endcall

//> if 'eq' in type_def.deriving and type_def.fields:
    friend bool operator==(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs);
    friend bool operator!=(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs);
//> endif
//> if 'ord' in type_def.deriving and type_def.fields
    friend bool operator<(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs);
    friend bool operator>(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs);
    friend bool operator<=(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs);
    friend bool operator>=(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs);
//> endif
};
//> if config.string_serialization and not type_def.cpp.base_type:
//> call disable_deprecation_warnings(type_def.deprecated)
std::string to_string(const {{ type_def.cpp.typename }}& value);
//> endcall
//> endif
//> endblock
//> block global
//> if config.string_serialization and not type_def.cpp.base_type:
//> call disable_deprecation_warnings(type_def.deprecated)
template<>
struct std::formatter<{{ type_def.cpp.typename }}> : std::formatter<std::string> {
    template<typename FormatContext>
    auto format(const {{ type_def.cpp.typename }}& value, FormatContext &ctx) const {
        return std::format_to(ctx.out(), "{}", {{ type_def.cpp.namespace }}::to_string(value));
    }
};
//> endcall
//> endif
//> endblock
