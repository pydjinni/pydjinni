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
{{ type_def.cppcli.return_typename }} {{ type_def.cppcli.delegate_name }}CppProxy::Invoke(
//> for param in type_def.parameters:
    {{ param.cppcli.typename }} {{ param.cppcli.name ~ (", " if not loop.last) }}
//> endfor
) {
    //> call cpp_error_handling(type_def)
    {{ "auto cpp_result = " if type_def.return_type_ref }}(*_lambda)(
        //> for param in type_def.parameters:
        {{ param.cppcli.translator }}::ToCpp({{ param.cppcli.name }}){{ "," if not loop.last }}
        //> endfor
    );
    //> if type_def.return_type_ref:
    return {{ type_def.return_type_ref.type_def.cppcli.translator }}::FromCpp(cpp_result);
    //> endif
    //> endcall
}

{{ type_def.cppcli.delegate_name }}CppProxy::~{{ type_def.cppcli.delegate_name }}CppProxy()
{
    this->!{{ type_def.cppcli.delegate_name }}CppProxy();
}

{{ type_def.cppcli.delegate_name }}CppProxy::!{{ type_def.cppcli.delegate_name }}CppProxy()
{
    delete _lambda;
}

{{ type_def.cppcli.delegate_name }}::CppType {{ type_def.cppcli.delegate_name }}::ToCpp(gcroot<{{ type_def.cppcli.delegate_name }}::CsType> delegate)
{
    if(static_cast<{{ type_def.cppcli.delegate_name }}::CsType>(delegate) != nullptr) {
        return [delegate](
        /*>- for param in type_def.parameters -*/
            {{ param.cpp.type_spec }} {{ param.cpp.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
        ){
            //> call cppcli_error_handling(type_def)
            {{ "auto cs_result = " if type_def.return_type_ref }}delegate->Invoke(
                //> for param in type_def.parameters:
                {{ param.cppcli.translator }}::FromCpp({{ param.cpp.name }}){{ "," if not loop.last }}
                //> endfor
            );
            //> if type_def.return_type_ref:
            return {{ type_def.return_type_ref.type_def.cppcli.translator }}::ToCpp(cs_result);
            //> endif
            //> endcall
        };
    } else return nullptr;

}

{{ type_def.cppcli.delegate_name }}::CsType {{ type_def.cppcli.delegate_name }}::FromCppOpt(const {{ type_def.cppcli.delegate_name }}::CppOptType& function) {
    if(function) {
        auto wrapper = gcnew {{ type_def.cppcli.delegate_name }}CppProxy(function);
        return gcnew {{ type_def.cppcli.typename }}(wrapper, &{{ type_def.cppcli.delegate_name }}CppProxy::Invoke);
    } else return nullptr;
}

{{ type_def.cppcli.delegate_name }}::CsType {{ type_def.cppcli.delegate_name }}::FromCpp(const {{ type_def.cppcli.delegate_name }}::CppType& function) { return FromCppOpt(function); }

//> endblock
