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
//> if not type_def.anonymous:
//? type_def.cppcli.comment : type_def.cppcli.comment | comment
//? type_def.deprecated : type_def.cppcli.deprecated
//? type_def.cppcli.nullability_attribute : type_def.cppcli.nullability_attribute
public delegate {{ type_def.cppcli.return_typename }} {{ type_def.cppcli.name }}(
    /*>- for param in type_def.parameters -*/
        {{ param.cppcli.nullability_attribute ~ param.cppcli.typename }} {{ param.cppcli.name ~ (", " if not loop.last)}}
    /*>- endfor -*/
);
//> endif

ref class {{ type_def.cppcli.delegate_name }}CppProxy
{
public:
    {{ type_def.cppcli.delegate_name }}CppProxy(const {{ type_def.cpp.typename }}& lambda) : _lambda(new {{ type_def.cpp.typename }}(lambda)) {}
    ~{{ type_def.cppcli.delegate_name }}CppProxy();
    !{{ type_def.cppcli.delegate_name }}CppProxy();

    {{ type_def.cppcli.return_typename }} Invoke(
    /*>- for param in type_def.parameters -*/
        {{ param.cppcli.typename }} {{ param.cppcli.name ~ (", " if not loop.last) }}
    /*>- endfor -*/
    );
private:
    {{ type_def.cpp.typename }}* _lambda;
};

class {{ type_def.cppcli.delegate_name }} {
public:
    using CppType = {{ type_def.cpp.typename }};
    using CppOptType = {{ type_def.cpp.typename }};
    using CsType = {{ type_def.cppcli.typename }}^;

    static CppType ToCpp(gcroot<CsType> delegate);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp);
};
//> endblock
