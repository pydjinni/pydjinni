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
//> if 'eq' in type_def.deriving:
bool operator==(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs) {
    return
    /*>- for field in type_def.fields */
{{ " " * 11 if not loop.first else " " }}lhs.{{ field.cpp.name }} == rhs.{{ field.cpp.name ~ (";" if loop.last else " &&") }}
    /*> endfor */
}
bool operator!=(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs) {
    return !(lhs == rhs);
}
//> endif
//> if 'ord' in type_def.deriving:
bool operator<(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs) {
    //> for field in type_def.fields
    if (lhs.{{ field.cpp.name }} < rhs.{{ field.cpp.name }}) {
        return true;
    }
    if (rhs.{{ field.cpp.name }} < lhs.{{ field.cpp.name }}) {
        return false;
    }
    //> endfor
    return false;
}

bool operator>(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs) {
    return rhs < lhs;
}

bool operator<=(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs) {
    return !(rhs < lhs);
}

bool operator>=(const {{ type_def.cpp.name }}& lhs, const {{ type_def.cpp.name }}& rhs) {
    return !(lhs < rhs);
}
//> endif
//> if 'str' in type_def.deriving:
//> call disable_deprecation_warnings(type_def.deprecated or (type_def.fields | map(attribute='deprecated') | any))
std::string to_string(const {{ type_def.cpp.typename }}& value) {
    //> for field in type_def.fields if field.type_ref.optional:
    //> if field.type_ref.type_def.primitive == 'collection':
    #ifndef __cpp_lib_format_ranges // gcc doesn't support ranges formatting yet as of Jan 2025
    auto {{ field.cpp.name }}_val = "{?}";
    #else
    //> endif
    auto {{ field.cpp.name }}_val = value.{{ field.cpp.name }}.has_value() ? std::format("{}", value.{{ field.cpp.name }}.value()) : "null";
    //> if field.type_ref.type_def.primitive == 'collection':
    #endif
    //> endif
    //> endfor
    return std::format("{{ type_def.cpp.typename }}(
        /*>- for field in type_def.fields -*/
        {{ field.cpp.name }}={}{{ ", " if not loop.last }}
        /*>- endfor */)",
        //> for field in type_def.fields
        //> if field.type_ref.optional
        {{ field.cpp.name }}_val{{ ", " if not loop.last }}
        //> else
        //> if field.type_ref.type_def.primitive == 'collection':
        #ifndef __cpp_lib_format_ranges // gcc doesn't support ranges formatting yet as of Jan 2025
        "{?}"{{ ", " if not loop.last }}
        #else
        //> endif
        value.{{ field.cpp.name }}{{ ", " if not loop.last }}
        //> if field.type_ref.type_def.primitive == 'collection':
        #endif
        //> endif
        //> endif
        //> endfor
    );
}
//> endcall
//> endif
//> endblock
