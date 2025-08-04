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
class {{ type_def.cpp.deprecated ~ type_def.cpp.name }} {
//> for property in type_def.properties
    pydjinni::signals::signal<{{ property.cpp.type_spec }}> _signal_{{ property.cpp.name }}_changed;
    {{ property.cpp.return_type_spec }} _{{ property.cpp.name }};
//> endfor
public:
    virtual ~{{ type_def.cpp.name }}() = default;
//> for method in type_def.methods
    //? method.comment : method.cpp.comment | comment | indent
    //? method.deprecated : method.cpp.deprecated
    {{ method.cpp.prefix_specifiers() ~ method.cpp.type_spec }} {{ method.cpp.name }}(
    /*>- for parameter in method.parameters -*/
        {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
    /*>- endfor */){{ method.cpp.postfix_specifiers() }};
//> endfor
//> for property in type_def.properties
    //? property.comment : property.cpp.comment | comment | indent
    //? property.deprecated : property.cpp.deprecated
    [[nodiscard]] {{ property.cpp.return_type_spec }} {{ property.cpp.getter }}() const noexcept;
    //? property.comment : property.cpp.comment | comment | indent
    //? property.deprecated : property.cpp.deprecated
    pydjinni::signals::connection {{ property.cpp.notifier }}(const std::function<void({{ property.cpp.type_spec }})>& callback) noexcept;
//? property.readonly : "protected:"
    //? property.comment : property.cpp.comment | comment | indent
    //? property.deprecated : property.cpp.deprecated
    virtual void {{ property.cpp.setter }}({{ property.cpp.type_spec }} value) noexcept;
//? property.readonly : "public:"
//> endfor
};
//> endblock
