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
    {{ method.cpp.signature }};
//> endfor
//> for property in type_def.properties
    //? property.comment : property.cpp.comment | comment | indent
    //? property.deprecated : property.cpp.deprecated
    [[nodiscard]] {{ property.cpp.getter_signature }};
    //? property.comment : property.cpp.comment | comment | indent
    //? property.deprecated : property.cpp.deprecated
    {{ property.cpp.notifier_signature }};
//? property.readonly : "protected:"
    //? property.comment : property.cpp.comment | comment | indent
    //? property.deprecated : property.cpp.deprecated
    virtual {{ property.cpp.setter_signature }};
//? property.readonly : "public:"
//> endfor
};
//> endblock
