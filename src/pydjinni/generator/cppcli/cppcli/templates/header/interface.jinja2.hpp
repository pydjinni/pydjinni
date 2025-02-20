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
public ref class {{ type_def.cppcli.name }} abstract {
public:
    //> for method in type_def.methods:
    //? method.cppcli.comment : method.cppcli.comment | comment | indent
    //? method.deprecated : method.cppcli.deprecated
    //? method.cppcli.nullability_attribute : method.cppcli.nullability_attribute
    {{ "static " if method.static else "virtual " }}{{ method.cppcli.typename }} {{ method.cppcli.name }}(
    /*>- for param in method.parameters -*/
        {{ param.cppcli.nullability_attribute ~ param.cppcli.typename }} {{ param.cppcli.name ~ (", " if not loop.last) }}
    /*>- endfor -*/
    ){{ " abstract" if not method.static }};
    //> endfor
internal:
    //? type_def.deprecated : "#pragma warning(suppress : 4996)"
    using CppType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    //? type_def.deprecated : "#pragma warning(suppress : 4996)"
    using CppOptType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    using CsType = {{ type_def.cppcli.name }}^;

    static CppType ToCpp(CsType cs);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp) { return FromCppOpt(cpp); }
    //> for method in type_def.methods if method.asynchronous and not method.static:
    ref class {{ method.cppcli.name }}CallbackHandleProxy {
    public:
        {{ method.cppcli.name }}CallbackHandleProxy(::pydjinni::coroutine::CallbackHandle<{{ method.cpp.callback_type_spec }}>& handle);
        void HandleCallback(System::Threading::Tasks::Task
        /*>- if method.return_type_ref -*/
        <{{ method.cppcli.synchronous_typename }}>
        /*>- endif -*/^ task);
    private:
        ::pydjinni::coroutine::CallbackHandle<{{ method.cpp.callback_type_spec }}>* _handle;
    };
    //> endfor
};
//> endblock
