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
//> set counter = namespace(value=0)

//> block content
//? type_def.comment : type_def.cpp.comment | comment
enum class {{ type_def.cpp.deprecated ~ type_def.cpp.name }} : unsigned {
//> for flag in type_def.flags:
    //? flag.comment : comment(flag.cpp.comment) | indent
    {{ flag.cpp.name ~ flag.cpp.deprecated ~ " = " -}}
    /*> if flag.none */
        {{- "0" -}}
    /*> elif flag.all */
        {{- "0 | " -}}
        /*> for flag in type_def.flags if not flag.none and not flag.all */
            {{- flag.cpp.name ~ (" | " if not loop.last) -}}
        /*> endfor */
    /*> else */
        {{- "1u << " ~ counter.value -}}
        /*> set counter.value = counter.value + 1 */
    /*> endif */
    {{- ("," if not loop.last) }}
//> endfor
};

constexpr {{ type_def.cpp.name }} operator|({{ type_def.cpp.name }} lhs, {{ type_def.cpp.name }} rhs) noexcept {
    return static_cast<{{ type_def.cpp.typename }}>(static_cast<unsigned>(lhs) | static_cast<unsigned>(rhs));
}
inline {{ type_def.cpp.name }}& operator|=({{ type_def.cpp.name }}& lhs, {{ type_def.cpp.name }} rhs) noexcept {
    return lhs = lhs | rhs;
}
constexpr {{ type_def.cpp.name }} operator&({{ type_def.cpp.name }} lhs, {{ type_def.cpp.name }} rhs) noexcept {
    return static_cast<{{ type_def.cpp.name }}>(static_cast<unsigned>(lhs) & static_cast<unsigned>(rhs));
}
inline {{ type_def.cpp.name }}& operator&=({{ type_def.cpp.name }}& lhs, {{ type_def.cpp.name }} rhs) noexcept {
    return lhs = lhs & rhs;
}
constexpr {{ type_def.cpp.name }} operator^({{ type_def.cpp.name }} lhs, {{ type_def.cpp.name }} rhs) noexcept {
    return static_cast<{{ type_def.cpp.name }}>(static_cast<unsigned>(lhs) ^ static_cast<unsigned>(rhs));
}
inline {{ type_def.cpp.name }}& operator^=({{ type_def.cpp.name }}& lhs, {{ type_def.cpp.name }} rhs) noexcept {
    return lhs = lhs ^ rhs;
}
constexpr {{ type_def.cpp.name }} operator~({{ type_def.cpp.name }} x) noexcept {
    return static_cast<{{ type_def.cpp.name }}>(~static_cast<unsigned>(x));
}
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
