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
//> from "macros.jinja2" import translator

//> block content
{{ type_def.jni.name }}::{{ type_def.jni.name }}() : ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.name }}>(
/*>- if 'cpp' in type_def.targets -*/
"{{ type_def.jni.class_descriptor }}$CppProxy"
/*>- endif -*/) {}
{{ type_def.jni.name }}::~{{ type_def.jni.name }}() = default;

//> if 'java' in type_def.targets:
{{ type_def.jni.name }}::JavaProxy::JavaProxy(JniType j) : Handle(::pydjinni::jniGetThreadEnv(), j) {}
{{ type_def.jni.name }}::JavaProxy::~JavaProxy() = default;

//> for method in type_def.methods:
{{ method.cpp.prefix_specifiers(implementation=True) ~ method.cpp.type_spec }} {{ type_def.jni.name }}::JavaProxy::{{ method.cpp.name }}(
/*>- for parameter in method.parameters -*/
    {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
/*>- endfor -*/
){{ method.cpp.postfix_specifiers(implementation=True) }} {
    //> if method.asynchronous:
    co_return co_await pydjinni::coroutine::CallbackAwaitable<{{ method.cpp.callback_type_spec }}>([&](pydjinni::coroutine::CallbackHandle<{{ method.cpp.callback_type_spec }}>& handle){
    //> endif
    auto jniEnv = ::pydjinni::jniGetThreadEnv();
    ::pydjinni::JniLocalScope jscope(jniEnv, 10);
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get();
    {{ "auto jret = " if method.return_type_ref or method.asynchronous }}jniEnv->{{ method.jni.routine_name }}(Handle::get().get(), data.method_{{ method.java.name }}
    /*>- for parameter in method.parameters -*/
        , ::pydjinni::get({{ translator(parameter.type_ref) }}::fromCpp(jniEnv, {{ parameter.cpp.name }}))
    /*>- endfor -*/
    );
    //> if method.throwing and not method.asynchronous:
    const ::pydjinni::LocalRef<jthrowable> e(jniEnv->ExceptionOccurred());
    if(e) {
        jniEnv->ExceptionClear();
        //> for error_domain_ref in method.throwing:
        //> set error_domain = error_domain_ref.type_def
        //> for error_code in error_domain.error_codes:
        {{ "else " if not loop.first }}if(jniEnv->IsInstanceOf(e.get(), ::pydjinni::jniFindClass("{{ error_domain.jni.class_descriptor }}${{ error_code.java.name }}").get())) {
            throw ::{{ error_domain.jni.namespace }}::{{ error_domain.jni.name }}::{{ error_code.jni.name }}::toCpp(jniEnv, e);
        }
        //> endfor
        //> endfor
        else {
            ::pydjinni::jniThrowCppFromJavaException(jniEnv, e.get());
        }
    }
    //> else:
    ::pydjinni::jniExceptionCheck(jniEnv);
    //> endif
    //> if method.return_type_ref and not method.asynchronous:
    return {{ translator(method.return_type_ref) }}::toCpp(jniEnv, jret);
    //> endif
    //> if method.asynchronous:
    auto completableFutureClass = ::pydjinni::jniFindClass("java/util/concurrent/CompletableFuture");
    auto completionMethod = ::pydjinni::jniGetMethodID(completableFutureClass.get(), "whenComplete", "(Ljava/util/function/BiConsumer;)Ljava/util/concurrent/CompletableFuture;");
    jniEnv->CallObjectMethod(jret, completionMethod, schedule::NativeCompletion::fromCpp(jniEnv, {
        .onSuccess = [&handle](jobject result) -> void {
            //> if method.return_type_ref:
            auto jniEnv = ::pydjinni::jniGetThreadEnv();
            handle.resume({{ method.jni.return_type_translator }}::toCpp(jniEnv, result));
            //> else:
            handle.resume();
            //> endif
        },
        .onError = [&handle](jthrowable exception) -> void {
            auto jniEnv = ::pydjinni::jniGetThreadEnv();
            jmethodID getCause = jniEnv->GetMethodID(::pydjinni::jniFindClass("java/lang/Throwable").get(), "getCause", "()Ljava/lang/Throwable;");
            jthrowable cause = (jthrowable)jniEnv->CallObjectMethod(exception, getCause);
            ::pydjinni::jniExceptionCheck(jniEnv);
            //> if method.throwing:
            //> for error_domain_ref in method.throwing:
            //> set error_domain = error_domain_ref.type_def
            //> for error_code in error_domain.error_codes:
            {{ "else " if not loop.first }}if(jniEnv->IsInstanceOf(cause, ::pydjinni::jniFindClass("{{ error_domain.jni.class_descriptor }}${{ error_code.java.name }}").get())) {
                handle.error(std::make_exception_ptr(::{{ error_domain.jni.namespace }}::{{ error_domain.jni.name }}::{{ error_code.jni.name }}::toCpp(jniEnv, cause)));
                return;
            }
            //> endfor
            //> endfor
            //> endif
            auto exceptionClass = ::pydjinni::jniFindClass("java/lang/Throwable");
            jmethodID getMessage = ::pydjinni::jniGetMethodID(exceptionClass.get(), "getMessage", "()Ljava/lang/String;");
            handle.error(std::make_exception_ptr(std::runtime_error(::pydjinni::jni::translator::String::toCpp(jniEnv, (jstring)jniEnv->CallObjectMethod(cause, getMessage)))));
        }
    }).get());
    ::pydjinni::jniExceptionCheck(jniEnv);
    });
    //> endif
}
//> endfor
//> endif

//> if 'cpp' in type_def.targets:
extern "C" {

[[maybe_unused]] JNIEXPORT void JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_00024CleanupTask_nativeDestroy(JNIEnv* jniEnv, jobject /*this*/, jlong nativeRef) noexcept {
    ::pydjinni::translate_exceptions(jniEnv, [&](){
        //? type_def.deprecated : "PYDJINNI_DISABLE_DEPRECATED_WARNINGS"
        delete reinterpret_cast<::pydjinni::CppProxyHandle<{{ type_def.cpp.typename }}>*>(nativeRef);
        //? type_def.deprecated : "PYDJINNI_ENABLE_WARNINGS"
    });
}

//> for method in type_def.methods:
[[maybe_unused]] JNIEXPORT {{ method.jni.return_type_spec }} JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_{{ "native_1" if not method.static }}{{ method.jni.name }}(JNIEnv* jniEnv, {{ "jclass" if method.static else "jobject, jlong nativeRef" }}
    /*>- for parameter in method.parameters -*/
    , {{ parameter.type_ref.type_def.jni.typename.value }} {{ parameter.jni.name }}
    /*>- endfor -*/
    ) noexcept {
    {{ "return " if method.return_type_ref or method.asynchronous }}::pydjinni::translate_exceptions(jniEnv, [&](){
        //> if method.asynchronous:
        auto completableFutureLocalRef = ::pydjinni::jniNewCompletableFuture(jniEnv);
        auto completableFuture = jniEnv->NewGlobalRef(completableFutureLocalRef.get());
        //> elif method.throwing:
        try {
        //> endif
        //? type_def.deprecated or method.deprecated : "PYDJINNI_DISABLE_DEPRECATED_WARNINGS"
        //> if method.static:
        {{ "auto r = " if (method.return_type_ref and not method.asynchronous) }}{{ type_def.cpp.typename }}::{{ method.cpp.name }}(
        //> else:
        const auto& ref = ::pydjinni::objectFromHandleAddress<{{ type_def.cpp.typename }}>(nativeRef);
        {{ "auto r = " if (method.return_type_ref and not method.asynchronous) }}ref->{{ method.cpp.name }}(
        /*>- endif -*/
        /*>- for parameter in method.parameters -*/
        {{ translator(parameter.type_ref) }}::toCpp(jniEnv, {{ parameter.jni.name }}){{ ", " if not loop.last }}
        /*>- endfor -*/
        )
        /*>- if method.asynchronous -*/
        .on_success([completableFuture]({{ (method.cpp.callback_type_spec ~ " r") if method.return_type_ref }}) -> void {
            auto jniEnv = ::pydjinni::jniGetThreadEnv();
            auto complete = ::pydjinni::jniGetCompletableFutureCompleteMethodID();
            jniEnv->CallBooleanMethod(completableFuture, complete,
            /*>- if method.return_type_ref -*/
                ::pydjinni::release({{ method.jni.return_type_translator }}::fromCpp(jniEnv, r))
            /*>- else -*/
                nullptr
            /*>- endif -*/);
            jniEnv->DeleteGlobalRef(completableFuture);
        }).on_error([completableFuture](const std::exception_ptr& e) -> void {
            auto jniEnv = ::pydjinni::jniGetThreadEnv();
            auto completeExceptionally = ::pydjinni::jniGetCompletableFutureCompleteExceptionallyMethodID();
            try { std::rethrow_exception(e); }
            /*> if method.throwing */
            /*> for error_domain_ref in method.throwing */
            /*> set error_domain = error_domain_ref.type_def */
            /*> for error_code in error_domain.error_codes */
            catch(const {{ error_domain.cpp.typename }}::{{ error_code.cpp.name }}& e) {
                jniEnv->CallBooleanMethod(completableFuture, completeExceptionally, ::pydjinni::get({{ error_domain.jni.translator }}::{{ error_code.jni.name }}::fromCpp(jniEnv, e)));
            }
            /*> endfor */
            /*> endfor */
            /*> endif */
            catch (const std::exception & e) {
                jniEnv->CallBooleanMethod(completableFuture, completeExceptionally, ::pydjinni::jniNewThrowable(jniEnv, ::pydjinni::release(::pydjinni::jni::translator::String::fromCpp(jniEnv, e.what()))));
            }
            jniEnv->DeleteGlobalRef(completableFuture);
        })
        .run(schedule::forkJoinPool)
        /*>- endif -*/
        ;
        //> if method.asynchronous:
         return ::pydjinni::release(completableFutureLocalRef);
        //> else:
            //> if method.return_type_ref:
            return ::pydjinni::release({{ method.jni.return_type_translator }}::fromCpp(jniEnv, r));
            //> endif
            //> if method.throwing:
            }
            //> for error_domain_ref in method.throwing:
            //> set error_domain = error_domain_ref.type_def
            //> for error_code in error_domain.error_codes:
            catch (const {{ error_domain.cpp.typename }}::{{ error_code.cpp.name }}& e) {
                jniEnv->Throw((jthrowable)::pydjinni::get({{ error_domain.jni.translator }}::{{ error_code.jni.name }}::fromCpp(jniEnv, e)));
            }
            //> endfor
            //> endfor
            //> endif
        //> endif
        //? type_def.deprecated or method.deprecated : "PYDJINNI_ENABLE_WARNINGS"
    });
}
//> endfor
}
//> endif
//> endblock
