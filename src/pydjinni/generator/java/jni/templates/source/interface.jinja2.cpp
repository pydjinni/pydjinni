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
//> macro coroutine(method)
//> if method.asynchronous:
    co_return co_await pydjinni::coroutine::CallbackAwaitable<{{ method.cpp.callback_type_spec }}>([&](pydjinni::coroutine::CallbackHandle<{{ method.cpp.callback_type_spec }}>& handle) -> void {
    {{ caller() | indent }}
    });
//> else:
{{ caller() }}
//> endif
//> endmacro

//> block content
{{ type_def.jni.name }}::{{ type_def.jni.name }}() : ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.name }}>(
/*>- if 'cpp' in type_def.targets -*/
"{{ type_def.jni.class_descriptor }}$CppProxy"
/*>- endif -*/) {}
{{ type_def.jni.name }}::~{{ type_def.jni.name }}() = default;

//> if 'java' in type_def.targets:
{{ type_def.jni.name }}::JavaProxy::JavaProxy(JniType j) : Handle(::pydjinni::jniGetThreadEnv(), j) {
    //> if type_def.properties:
    ::pydjinni::jni::ScopedJni jni {};
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get();
    //> for property in type_def.properties:
    _{{ property.jni.name }}_connection = ::pydjinni::GlobalRef<jobject>(
        jni.env, 
        jni.env->CallObjectMethod(Handle::get().get(), data.property_{{ property.jni.name }}_notifier, ::pydjinni::get(::pydjinni::jni::OnPropertyChangedCallback::fromCpp(
            jni.env, 
            std::make_shared<::pydjinni::jni::OnPropertyChangedCallbackCppWrapper>(
                [&](const ::pydjinni::GlobalRef<jobject>& value){
                    ::pydjinni::jni::ScopedJni jni {};
                    {{ property.cpp.notifier }}_handler({{ property.jni.translator }}::Boxed::toCpp(jni.env, ({{ property.jni.translator }}::Boxed::JniType) value.get()));
                }
            )
        )))
    );
    if(const auto& e = jni.ExceptionOccurred()) {
        jni.Terminate(e);
    }
    //> endfor
    //> endif
}
{{ type_def.jni.name }}::JavaProxy::~JavaProxy() = default;

//> for property in type_def.properties:
void {{ type_def.jni.name }}::JavaProxy::{{ property.cpp.setter }}({{ property.cpp.type_spec }} value) noexcept {
    ::pydjinni::jni::ScopedJni jni {};
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get();
    jni.env->CallVoidMethod(Handle::get().get(), data.property_{{ property.jni.name }}_setter, ::pydjinni::get({{ property.jni.translator }}::fromCpp(jni.env, value)));
    if(const auto& e = jni.ExceptionOccurred()) {
        jni.Terminate(e);
    }
}

void {{ type_def.jni.name }}::JavaProxy::{{ property.cpp.notifier }}_handler({{ property.cpp.type_spec }} value) noexcept {
    {{ type_def.jni.name }}::{{ property.cpp.setter }}(value);
}
//> endfor
//> for method in type_def.methods:
{{ method.cpp.prefix_specifiers(implementation=True) ~ method.cpp.type_spec }} {{ type_def.jni.name }}::JavaProxy::{{ method.cpp.name }}(
/*>- for parameter in method.parameters -*/
    {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
/*>- endfor -*/
){{ method.cpp.postfix_specifiers(implementation=True) }} {
    //> call coroutine(method):
    ::pydjinni::jni::ScopedJni jni {};
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get();
    {{ "auto jret = " if method.return_type_ref or method.asynchronous }}jni.env->{{ method.jni.routine_name }}(Handle::get().get(), data.method_{{ method.jni.name }}
    /*>- for parameter in method.parameters -*/
        , ::pydjinni::get({{ parameter.jni.translator }}::fromCpp(jni.env, {{ parameter.cpp.name }}))
    /*>- endfor -*/
    );
    {{ jni_error_handling(method) | indent }}
    //> if method.return_type_ref and not method.asynchronous:
    return {{ method.jni.return_type_translator }}::toCpp(jni.env, jret);
    //> endif
    //> if method.asynchronous:
    jni.Get<::pydjinni::jni::Jni::CompletableFuture>(jret).WhenComplete({
        .onSuccess = [&handle](jobject result) -> void {
            //> if method.return_type_ref:
            auto jniEnv = ::pydjinni::jniGetThreadEnv();
            handle.resume({{ method.jni.return_type_translator }}::Boxed::toCpp(jniEnv, result));
            //> else:
            handle.resume();
            //> endif
        },
        .onError = [&handle](jthrowable exception) -> void {
            ::pydjinni::jni::Jni jni {};
            const auto cause = jni.Get<::pydjinni::jni::Jni::Throwable>(exception).GetCause();
            //> if method.throwing:
            //> for error_domain_ref in method.throwing:
            //> set error_domain = error_domain_ref.type_def
            //> for error_code in error_domain.error_codes:
            {{ "else " if not loop.first }}if(jni.IsInstanceOf<::{{ error_domain.jni.namespace }}::{{ error_domain.jni.name }}::{{ error_code.jni.name }}>(cause)) {
                handle.error(std::make_exception_ptr(::{{ error_domain.jni.namespace }}::{{ error_domain.jni.name }}::{{ error_code.jni.name }}::toCpp(jni.env, cause)));
                return;
            }
            //> endfor
            //> endfor
            else {
                handle.error(std::make_exception_ptr(::pydjinni::jni_exception{jni.env, cause}));
            }
            //> else
            handle.error(std::make_exception_ptr(::pydjinni::jni_exception{jni.env, cause}));
            //> endif

        }
    });
    //> endif
    //> endcall
}
//> endfor
//> endif

//> if 'cpp' in type_def.targets:
extern "C" {

[[maybe_unused]] JNIEXPORT void JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_00024CleanupTask_nativeDestroy(JNIEnv* jniEnv, jobject /*this*/, jlong nativeRef) noexcept {
     //? type_def.deprecated : "PYDJINNI_DISABLE_DEPRECATED_WARNINGS"
    delete reinterpret_cast<::pydjinni::CppProxyHandle<{{ type_def.cpp.typename }}>*>(nativeRef);
    //? type_def.deprecated : "PYDJINNI_ENABLE_WARNINGS"
}

//> for property in type_def.properties:
[[maybe_unused]] JNIEXPORT {{ property.jni.typename }} JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_native_1{{ property.java.getter }}(JNIEnv* jniEnv, jobject, jlong nativeRef) {
    const ::pydjinni::jni::Jni jni { jniEnv };
    const auto& ref = ::pydjinni::objectFromHandleAddress<{{ type_def.cpp.typename }}>(nativeRef);
    return ::pydjinni::release({{ property.jni.translator }}::fromCpp(jni.env, ref->{{ property.cpp.getter }}()));
}

[[maybe_unused]] JNIEXPORT jobject JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_native_1{{ property.java.notifier }}(JNIEnv* jniEnv, jobject, jlong nativeRef, jobject callback) {
    const ::pydjinni::jni::Jni jni { jniEnv };
    const auto& ref = ::pydjinni::objectFromHandleAddress<{{ type_def.cpp.typename }}>(nativeRef);
    const auto globalRef = ::pydjinni::GlobalRef<jobject> { jni.env, callback };
    return ::pydjinni::release(pydjinni::jni::NativeConnection::fromCpp(jni.env, std::move(ref->{{ property.cpp.notifier }}([globalRef]({{ property.cpp.type_spec }} value){
         const auto localEnv = ::pydjinni::jniGetThreadEnv();
         const auto clazz = localEnv->FindClass("{{ callback_type }}");
         const auto methodId = localEnv->GetMethodID(clazz, "callback", "(Ljava/lang/Object;)V");
         localEnv->CallVoidMethod(globalRef.get(), methodId, ::pydjinni::get({{ property.jni.translator }}::Boxed::fromCpp(localEnv, value)));
    }))));
}

//> if not property.readonly:
[[maybe_unused]] JNIEXPORT void JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_native_1{{ property.java.setter }}(JNIEnv* jniEnv, jobject, jlong nativeRef, {{ property.jni.typename }} value) {
    const ::pydjinni::jni::Jni jni { jniEnv };
    const auto& ref = ::pydjinni::objectFromHandleAddress<{{ type_def.cpp.typename }}>(nativeRef);
    ref->{{ property.cpp.setter }}({{ property.jni.translator }}::toCpp(jni.env, value));
}
//> endif
//> endfor

//> for method in type_def.methods:
[[maybe_unused]] JNIEXPORT {{ method.jni.return_type_spec }} JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_{{ "native_1" if not method.static }}{{ method.jni.name }}(JNIEnv* jniEnv, {{ "jclass" if method.static else "jobject, jlong nativeRef" }}
    /*>- for parameter in method.parameters -*/
    , {{ parameter.jni.typename }} {{ parameter.jni.name }}
    /*>- endfor -*/
    ) noexcept {
    const ::pydjinni::jni::Jni jni { jniEnv };
    //> call cpp_error_handling(method)
    //> if method.asynchronous:
    auto future = jni.New<::pydjinni::jni::Jni::CompletableFuture>();
    //> endif
    //? type_def.deprecated or method.deprecated : "PYDJINNI_DISABLE_DEPRECATED_WARNINGS"
    //> if method.static:
    {{ "auto r = " if (method.return_type_ref and not method.asynchronous) }}{{ type_def.cpp.typename }}::{{ method.cpp.name }}(
    //>- else:
    const auto& ref = ::pydjinni::objectFromHandleAddress<{{ type_def.cpp.typename }}>(nativeRef);
    {{ "auto r = " if (method.return_type_ref and not method.asynchronous) }}ref->{{ method.cpp.name }}(
    /*>- endif -*/
    /*>- for parameter in method.parameters -*/
    {{ parameter.jni.translator }}::toCpp(jniEnv, {{ parameter.jni.name }}){{ ", " if not loop.last }}
    /*>- endfor -*/
    )
    /*>- if method.asynchronous -*/
    .on_success([handle = future.Handle()]({{ (method.cpp.callback_type_spec ~ " result") if method.return_type_ref }}) -> void {
        //> if method.return_type_ref:
        handle.Complete<{{ method.jni.return_type_translator }}>(result);
        //> else:
        handle.Complete();
        //> endif
    })/*> if not method.cpp.noexcept */.on_error([handle = future.Handle()](const std::exception_ptr& e) -> void {
        try { std::rethrow_exception(e); }
        /*> if method.throwing */
        /*> for error_domain_ref in method.throwing */
        /*> set error_domain = error_domain_ref.type_def */
        /*> for error_code in error_domain.error_codes */
        catch(const {{ error_domain.cpp.typename }}::{{ error_code.cpp.name }}& e) {
            handle.CompleteExceptionally<{{ error_domain.jni.translator }}::{{ error_code.jni.name }}>(e);
        }
        /*> endfor */
        /*> endfor */
        /*> endif */
        catch (const ::pydjinni::jni_exception& e) {
            handle.CompleteExceptionally(e);
        }
        catch (const std::exception & e) {
            handle.CompleteExceptionally(e);
        }
    })/*> endif */.run(schedule::forkJoinPool)
    /*>- endif -*/
    ;
    //> if method.asynchronous:
    return future.Return();
    //> else:
    //> if method.return_type_ref:
    return ::pydjinni::release({{ method.jni.return_type_translator }}::fromCpp(jni.env, r));
    //> endif
    //> endif
    //? type_def.deprecated or method.deprecated : "PYDJINNI_ENABLE_WARNINGS"
    //> endcall
}

//> endfor
}
//> endif
//> endblock
