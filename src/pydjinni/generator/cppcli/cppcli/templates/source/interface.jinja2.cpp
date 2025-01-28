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
//? type_def.deprecated or type_def.methods | map(attribute="deprecated") | any : "#pragma warning(disable : 4947 4996)"
//> if 'cpp' in type_def.targets
//> for method in type_def.methods if method.asynchronous:
static {{ method.cppcli.typename }} {{ method.cppcli.async_proxy_name }}(
    /*>- if not method.static -*/
        const std::shared_ptr<{{ type_def.cpp.typename }}>& handle
    /*>- endif -*/
    /*>- for param in method.parameters -*/
        {{ ", " if loop.first and not method.static }}{{ param.cppcli.typename }} {{ param.cppcli.name ~ (", " if not loop.last) }}
    /*>- endfor -*/
) {
    gcroot<System::Threading::Tasks::TaskCompletionSource<{{ method.cppcli.synchronous_typename if method.return_type_ref else "System::Object^" }}>^> completionSource = gcnew System::Threading::Tasks::TaskCompletionSource<{{ method.cppcli.synchronous_typename if method.return_type_ref else "System::Object^" }}>();
    {{ (type_def.cpp.typename ~ "::") if method.static else "handle->" }}{{ method.cpp.name }}(
    /*>- for param in method.parameters -*/
        {{ param.cppcli.translator }}::ToCpp({{ param.cppcli.name }}){{ ", " if not loop.last }}
    /*>- endfor -*/
    ).on_success([completionSource]({{ (method.cpp.callback_type_spec ~ " cpp_result") if method.return_type_ref }}){
        completionSource->SetResult({{ (method.cppcli.translator ~ "::FromCpp(cpp_result)") if method.return_type_ref else "nullptr" }});
    }).on_error([completionSource](const std::exception_ptr& e) {
        try { std::rethrow_exception(e); }
        //> if method.throwing:
        //> for type_ref in method.throwing:
        //> set error_domain = type_ref.type_def
        //> for error_code in error_domain.error_codes:
        catch (const {{ error_domain.cpp.typename }}::{{ error_code.cpp.name }}& e) {
            completionSource->SetException({{ error_domain.cppcli.typename }}::{{ error_code.cppcli.name }}::FromCpp(e));
        }
        //> endfor
        //> endfor
        //> endif
        catch (const std::exception& e) {
            completionSource->SetException(gcnew System::Exception(msclr::interop::marshal_as<System::String^>(e.what())));
        }
    }).run(::pydjinni::coroutine::schedule::dotnet);
    return completionSource->Task;
}
//> endfor
//> for method in type_def.methods if method.static:
{{ method.cppcli.typename }} {{ type_def.cppcli.name }}::{{ method.cppcli.name }}(
/*>- for param in method.parameters -*/
    {{ param.cppcli.typename }} {{ param.cppcli.name ~ (", " if not loop.last) }}
/*>- endfor -*/
)
{
    //> if method.asynchronous:
    return {{ method.cppcli.async_proxy_name }}(
    /*>- for param in method.parameters -*/
        {{ param.cppcli.name ~ (", " if not loop.last) }}
    /*>- endfor -*/
    );
    //> else:
    //> call cpp_error_handling(method)
    {{ "auto cpp_result = " if method.return_type_ref -}}
    {{ type_def.cpp.typename }}::{{ method.cpp.name }}(
    /*>- for param in method.parameters -*/
        {{ param.cppcli.translator }}::ToCpp({{ param.cppcli.name }}){{ "," if not loop.last }}
    /*>- endfor -*/);
    //> if method.return_type_ref:
    return {{ method.cppcli.translator }}::FromCpp(cpp_result);
    //> endif
    //> endcall
    //> endif
}
//> endfor

ref class {{ type_def.cppcli.name }}CppProxy : public {{ type_def.cppcli.name }} {
    using CppType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    using HandleType = ::pydjinni::CppProxyCache::Handle<CppType>;
public:
    {{ type_def.cppcli.name }}CppProxy(const CppType& cppRef) : _cppRefHandle(new HandleType(cppRef)) {}

    //> for method in type_def.methods if not method.static:
    {{ method.cppcli.typename }} {{ method.cppcli.name }}(
    /*>- for param in method.parameters -*/
        {{ param.cppcli.typename }} {{ param.cppcli.name ~ (", " if not loop.last) }}
    /*>- endfor -*/
    ) override
    {
        //> if method.asynchronous:
        return {{ method.cppcli.async_proxy_name }}(_cppRefHandle->get()
        /*>- for param in method.parameters -*/
            {{ (", " if loop.first) ~ param.cppcli.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
        );
        //> else:
        //> call cpp_error_handling(method)
        {{ "auto cpp_result = " if method.return_type_ref -}}
        {{- (type_def.cpp.coroutine_entrypoint ~ "(") if method.asynchronous -}}
        _cppRefHandle->get()->{{ method.cpp.name }}(
        //> for param in method.parameters
            {{ param.cppcli.translator }}::ToCpp({{ param.cppcli.name }}){{ ", " if not loop.last }}
        //> endfor
        ){{ ")" if method.asynchronous }};
        //> if method.return_type_ref
        return {{ method.cppcli.translator }}::FromCpp(cpp_result);
        //> endif
        //> endcall
        //> endif
    }
    //> endfor

    CppType djinni_private_get_proxied_cpp_object() {
        return _cppRefHandle->get();
    }

private:
    AutoPtr<HandleType> _cppRefHandle;
};
//> endif
//> if 'cppcli' in type_def.targets:
class {{ type_def.cppcli.name }}CsProxy : public {{ type_def.cpp.typename }} {
    using CsType = {{ type_def.cppcli.typename }}^;
    using CsRefType = ::pydjinni::CsRef<CsType>;
    using HandleType = ::pydjinni::CsProxyCache::Handle<::pydjinni::CsRef<CsType>>;
public:
    {{ type_def.cppcli.name }}CsProxy(CsRefType cs) : m_djinni_private_proxy_handle(std::move(cs)) {}
    {{ type_def.cppcli.name }}CsProxy(const ::pydjinni::CsRef<System::Object^>& ptr) : {{ type_def.cppcli.name }}CsProxy(CsRefType(dynamic_cast<CsType>(ptr.get()))) {}
    //> for method in type_def.methods:
    {{ method.cpp.prefix_specifiers(implementation=True) ~ method.cpp.type_spec }} {{ method.cpp.name }}(
    /*>- for param in method.parameters -*/
        {{ param.cpp.type_spec }} {{ param.cpp.name ~ (", " if not loop.last) }}
    /*>- endfor -*/
    ){{ method.cpp.postfix_specifiers(implementation=True) }} override
    {
        //> if method.asynchronous:
        {{ "co_return " if method.return_type_ref }}co_await ::pydjinni::coroutine::CallbackAwaitable<{{ method.cppcli.synchronous_typename }}>([&](::pydjinni::coroutine::CallbackHandle<{{ method.cppcli.synchronous_typename }}>& handle){
        //> endif
        //> if method.asynchronous:
        gcroot<System::Action<System::Threading::Tasks::Task{{ ("<" ~ method.cppcli.synchronous_typename ~ ">") if method.return_type_ref }}^>^> callbackAction = gcnew System::Action<System::Threading::Tasks::Task{{ ("<" ~ method.cppcli.synchronous_typename ~ ">") if method.return_type_ref }}^>(
            gcnew {{ type_def.cppcli.typename }}::{{ method.cppcli.name }}CallbackHandleProxy(handle),
            &{{ type_def.cppcli.typename }}::{{ method.cppcli.name }}CallbackHandleProxy::HandleCallback
        );
        //> endif
        //> call cppcli_error_handling(method)
        {{ "auto cs_result = " if method.return_type_ref.type_def or method.asynchronous -}}
        djinni_private_get_proxied_cs_object()->{{ method.cppcli.name }}(
        //> for param in method.parameters:
            {{ param.cppcli.translator }}::FromCpp({{ param.cpp.name }}){{ "," if not loop.last }}
        //> endfor
        )/*> if method.asynchronous */->ContinueWith(callbackAction)/*>- endif -*/;
        /*> if method.return_type_ref.type_def and not method.asynchronous */
        return {{ method.cppcli.translator }}::ToCpp(cs_result);
        //> endif
        //> endcall
        //> if method.asynchronous:
        });
        //> endif
    }
    //> endfor

    CsType djinni_private_get_proxied_cs_object() const {
        return m_djinni_private_proxy_handle.get().get();
    }
private:
    HandleType m_djinni_private_proxy_handle;
};
//> endif

{{ type_def.cppcli.name }}::CppType {{ type_def.cppcli.name }}::ToCpp({{ type_def.cppcli.name }}::CsType cs)
{
    if(!cs) {
        return nullptr;
    }
    //> if 'cppcli' in type_def.targets:
    //> if 'cpp' in type_def.targets:
    if (auto cs_ref = dynamic_cast<{{ type_def.cppcli.name }}CppProxy^>(cs))
    {
        return cs_ref->djinni_private_get_proxied_cpp_object();
    }
    //> endif
    return ::pydjinni::get_cs_proxy<{{ type_def.cppcli.name }}CsProxy>(cs);
    //> else:
    return dynamic_cast<{{ type_def.cppcli.name }}CppProxy^>(cs)->djinni_private_get_proxied_cpp_object();
    //> endif
}

{{ type_def.cppcli.name }}::CsType {{ type_def.cppcli.name }}::FromCppOpt(const {{ type_def.cppcli.name }}::CppOptType& cpp)
{
    if (!cpp) {
        return nullptr;
    }
    //> if 'cppcli' in type_def.targets:
    //> if 'cpp' in type_def.targets:
    if (auto cpp_ptr = dynamic_cast<{{ type_def.cppcli.name }}CsProxy*>(cpp.get())) {
        return cpp_ptr->djinni_private_get_proxied_cs_object();
    }
    return ::pydjinni::get_cpp_proxy<{{ type_def.cppcli.name }}CppProxy^>(cpp);
    //> else:
    return dynamic_cast<{{ type_def.cppcli.name }}CsProxy*>(cpp.get())->djinni_private_get_proxied_cs_object();
    //> endif
    //> else:
    return ::pydjinni::get_cpp_proxy<{{ type_def.cppcli.name }}CppProxy^>(cpp);
    //> endif
}

//> for method in type_def.methods if method.asynchronous and not method.static:
{{ type_def.cppcli.name }}::{{ method.cppcli.name }}CallbackHandleProxy::{{ method.cppcli.name }}CallbackHandleProxy(::pydjinni::coroutine::CallbackHandle<{{ method.cpp.callback_type_spec }}>& handle) : _handle(&handle) {}
void {{ type_def.cppcli.name }}::{{ method.cppcli.name }}CallbackHandleProxy::HandleCallback(System::Threading::Tasks::Task
/*>- if method.return_type_ref -*/
    <{{ method.cppcli.synchronous_typename }}>
/*>- endif -*/
^ task) {
    if (task->IsFaulted) {
        try {
            //> if method.throwing:
            //> for error_domain_ref in method.throwing:
            //> set error_domain = error_domain_ref.type_def
            //> for error_code in error_domain.error_codes:
            {{ "else " if not loop.first }}if(task->Exception->InnerException->GetType() == {{ error_domain.cppcli.typename }}::{{ error_code.cppcli.name }}::typeid)
            {
                throw {{ error_domain.cppcli.typename }}::{{ error_code.cppcli.name }}::ToCpp(safe_cast<{{ error_domain.cppcli.typename }}::{{ error_code.cppcli.name }}^>(task->Exception->InnerException));
            }
            //> endfor
            //> endfor
            //> endif
            throw std::runtime_error(::pydjinni::cppcli::translator::String::ToCpp(task->Exception->InnerException->Message));
        }
        catch (...) {
            _handle->error(std::current_exception());
        }
    }
    if(task->IsCompleted) _handle->resume(
    /*>- if method.return_type_ref -*/
        {{ method.cppcli.translator }}::ToCpp(task->Result)
    /*>- endif -*/
    );
}
//> endfor
//> endblock
