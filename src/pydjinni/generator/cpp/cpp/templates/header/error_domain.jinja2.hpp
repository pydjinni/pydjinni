/*#
Copyright 2024 jothepro

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
struct {{ type_def.cpp.deprecated ~ type_def.cpp.name }} : public std::exception {
    [[nodiscard]] const char * what() const noexcept override = 0;
    //> for error_code in type_def.error_codes:
    class {{ error_code.cpp.name }};
    //> endfor
};

//> for error_code in type_def.error_codes:
//? error_code.comment : error_code.cpp.comment | comment
//> call disable_deprecation_warnings(type_def.deprecated)
class {{ error_code.cpp.deprecated ~ type_def.cpp.name }}::{{ error_code.cpp.name }} final : public {{ type_def.cpp.name }} {
//> endcall
public:
    //> for parameter in error_code.parameters:
    //? parameter.comment : parameter.cpp.comment | comment | indent
    const {{ parameter.cpp.type_spec }} {{ parameter.cpp.name }};
    //> endfor
    //? error_code.cpp.constructor_comment : error_code.cpp.constructor_comment | comment | indent
    explicit {{ error_code.cpp.name }}(
        /*>- for parameter in error_code.parameters -*/
        {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ ", " }}
        /*>- endfor */std::string message = "")
        : /*> for parameter in error_code.parameters -*/
        {{ parameter.cpp.name }}(std::move({{ parameter.cpp.name }})){{ ", " }}
        /*>- endfor */message(std::move(message)) {}
    [[nodiscard]] const char * what() const noexcept override {
        return message.c_str();
    }
private:
    const std::string message;
};

//> endfor
//> endblock
