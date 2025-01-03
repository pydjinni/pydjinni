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
//? type_def.deprecated or type_def.error_codes | map(attribute="deprecated") | any : "#pragma warning(disable : 4947 4996)"
{{ type_def.cppcli.name }}::{{ type_def.cppcli.name }}() : System::Exception() {}
{{ type_def.cppcli.name }}::{{ type_def.cppcli.name }}(System::String^ message) : System::Exception(message) {}


//> for error_code in type_def.error_codes:
{{ type_def.cppcli.name }}::{{ error_code.cppcli.name }}::{{ error_code.cppcli.name }}(
/*>- for parameter in error_code.parameters -*/
    {{ parameter.cppcli.typename }} {{ parameter.cppcli.name ~ (", " if not loop.last) }}
/*>- endfor -*/)
/*>- for parameter in error_code.parameters -*/
{{ (": " if loop.first else ", ") ~ "_" ~ parameter.cppcli.name }}({{ parameter.cppcli.name }})
/*>- endfor -*/ {}

{{ type_def.cppcli.name }}::{{ error_code.cppcli.name }}::{{ error_code.cppcli.name }}(
/*>- for parameter in error_code.parameters -*/
    {{ parameter.cppcli.typename }} {{ parameter.cppcli.name ~ ", "}}
/*>- endfor -*/
System::String^ message) :
/*>- for parameter in error_code.parameters -*/
_{{ parameter.cppcli.name }}({{ parameter.cppcli.name }}){{ ", " }}
/*>- endfor -*/
{{ type_def.cppcli.name }}(message) {}

//> for parameter in error_code.parameters:
{{ parameter.cppcli.typename }} {{ type_def.cppcli.name }}::{{ error_code.cppcli.name }}::{{ parameter.cppcli.property }}::get()
{
    return _{{ parameter.cppcli.name }};
}
//> endfor

{{ type_def.cppcli.name }}::{{ error_code.cppcli.name }}::CppType {{ type_def.cppcli.name }}::{{ error_code.cppcli.name }}::ToCpp({{ error_code.cppcli.name }}::CsType cs)
{
    ASSERT(cs != nullptr);
    return {{ type_def.cppcli.name }}::{{ error_code.cppcli.name }}::CppType {
    //> for parameter in error_code.parameters:
        {{ parameter.cppcli.translator }}::ToCpp(cs->{{ parameter.cppcli.property }}),
    //> endfor
        ::pydjinni::cppcli::translator::String::ToCpp(cs->Message)
    };
}

{{ type_def.cppcli.name }}::{{ error_code.cppcli.name }}::CsType {{ type_def.cppcli.name }}::{{ error_code.cppcli.name }}::FromCpp(const {{ error_code.cppcli.name }}::CppType& cpp)
{
    return gcnew {{ error_code.cppcli.name }}(
    //> for parameter in error_code.parameters:
        {{ parameter.cppcli.translator }}::FromCpp(cpp.{{ parameter.cpp.name }}),
    //> endfor
        ::pydjinni::cppcli::translator::String::FromCpp(cpp.what())
    );
}
//> endfor
//> endblock
