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
//? type_def.cppcli.comment : type_def.cppcli.comment | comment
//? type_def.deprecated : type_def.cppcli.deprecated
public ref class {{ type_def.cppcli.name }} abstract : System::Exception {
public:
    {{ type_def.cppcli.name }}();
    {{ type_def.cppcli.name }}(System::String^ message);
    /*> for error_code in type_def.error_codes */
    ref class {{ error_code.cppcli.name }};
    /*> endfor */
};

//> for error_code in type_def.error_codes:
//? error_code.cppcli.comment : error_code.cppcli.comment | comment
//? error_code.deprecated : error_code.cppcli.deprecated
//? type_def.deprecated : "#pragma warning(suppress : 4947)"
ref class {{ type_def.cppcli.name }}::{{ error_code.cppcli.name }} : {{ type_def.cppcli.name }} {
public:
    {{ error_code.cppcli.name }}(
    /*>- for parameter in error_code.parameters -*/
        {{ parameter.cppcli.typename }} {{ parameter.cppcli.name ~ (", " if not loop.last) }}
    /*>- endfor -*/);
    {{ error_code.cppcli.name }}(
    /*>- for parameter in error_code.parameters -*/
        {{ parameter.cppcli.typename }} {{ parameter.cppcli.name ~ ", " }}
    /*>- endfor -*/
    System::String^ message);

    //> for parameter in error_code.parameters
    //? parameter.cppcli.comment : parameter.cppcli.comment | comment | indent
    property {{ parameter.cppcli.typename }} {{ parameter.cppcli.property }}
    {
        {{ parameter.cppcli.typename }} get();
    }
    //> endfor
internal:
    //? error_code.deprecated : "#pragma warning(suppress : 4996)"
    using CppType = ::{{ type_def.cpp.namespace }}::{{ type_def.cpp.name }}::{{ error_code.cpp.name }};
    using CsType = {{ error_code.cppcli.name }}^;

    static CppType ToCpp(CsType cs);
    static CsType FromCpp(const CppType& cpp);
private:
    //> for parameter in error_code.parameters
    {{ parameter.cppcli.typename }} _{{ parameter.cppcli.name }};
    //> endfor
};
//> endfor
//> endblock
