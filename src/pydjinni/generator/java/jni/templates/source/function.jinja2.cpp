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
//> from "macros.jinja2" import translator

//> block content
{{ type_def.cpp.typename}} {{ type_def.jni.name }}::toCpp(JNIEnv* jniEnv, JniType j){
    auto functional_class = ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get()._fromJava(jniEnv, j);
    return [functional_class](
        /*>- for parameter in type_def.parameters -*/
            {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
    ) -> {{ type_def.cpp.type_spec }} {
        {{ "return " if type_def.return_type_ref }}functional_class->invoke(
        /*>- for parameter in type_def.parameters -*/
            {{ parameter.cpp.name ~ (", " if not loop.last )}}
        /*>- endfor -*/
        );
    };
}

::pydjinni::LocalRef<{{ type_def.jni.name }}::JniType> {{ type_def.jni.name }}::fromCppOpt(JNIEnv* jniEnv, const {{ type_def.cpp.typename }}& c) {
    auto proxy = std::make_shared<{{ type_def.jni.name }}::CppProxy>(c);
    return {jniEnv, ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get()._toJava(jniEnv, proxy)};
}

::pydjinni::LocalRef<{{ type_def.jni.name }}::JniType> {{ type_def.jni.name }}::fromCpp(JNIEnv* jniEnv, const {{ type_def.cpp.typename }}& c) { return fromCppOpt(jniEnv, c); }


{{ type_def.jni.name }}::{{ type_def.jni.name }}() : ::pydjinni::JniInterface<{{ type_def.jni.wrapper }}, {{ type_def.jni.name }}>("{{ type_def.jni.class_descriptor }}CppProxy") {}
{{ type_def.jni.name }}::~{{ type_def.jni.name }}() = default;

//> if 'java' in type_def.targets:
{{ type_def.jni.name }}::JavaProxy::JavaProxy(JniType j) : Handle(::pydjinni::jniGetThreadEnv(), j) {}
{{ type_def.jni.name }}::JavaProxy::~JavaProxy() = default;


{{ type_def.cpp.type_spec }} {{ type_def.jni.name }}::JavaProxy::invoke(
/*>- for parameter in type_def.parameters -*/
    {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
/*>- endfor -*/
) {
    auto jniEnv = ::pydjinni::jniGetThreadEnv();
    ::pydjinni::JniLocalScope jscope(jniEnv, 10);
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get();
    {{ "auto jret = " if type_def.return_type_ref }}jniEnv->{{ type_def.jni.routine_name }}(Handle::get().get(), data.method_invoke
    /*>- for parameter in type_def.parameters -*/
        , ::pydjinni::get({{ translator(parameter.type_ref) }}::fromCpp(jniEnv, {{ parameter.cpp.name }}))
    /*>- endfor -*/
    );
    ::pydjinni::jniExceptionCheck(jniEnv);
    //> if type_def.return_type_ref:
    return {{ type_def.jni.return_type_translator }}::toCpp(jniEnv, jret);
    //> endif
}

//> endif

//> if 'cpp' in type_def.targets:
extern "C" {

[[maybe_unused]] JNIEXPORT void JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_00024CleanupTask_nativeDestroy(JNIEnv* jniEnv, jobject /*this*/, jlong nativeRef) noexcept {
    delete reinterpret_cast<::pydjinni::CppProxyHandle<{{ type_def.jni.wrapper }}>*>(nativeRef);
}

[[maybe_unused]] JNIEXPORT {{ type_def.jni.return_type_spec }} JNICALL {{ type_def.jni.jni_prefix }}CppProxy_nativeInvoke(JNIEnv* jniEnv, jobject /*this*/, jlong nativeRef
    /*>- for parameter in type_def.parameters -*/
    , {{ parameter.type_ref.type_def.jni.typename.value }} {{ parameter.jni.name }}
    /*>- endfor -*/
    ) noexcept {
    {{ "return" if type_def.return_type_ref }} ::pydjinni::translate_exceptions(jniEnv, [&](){
        const auto& ref = ::pydjinni::objectFromHandleAddress<{{ type_def.jni.wrapper }}>(nativeRef);
        {{ "auto r = " if type_def.return_type_ref }}ref->invoke(
            /*>- for parameter in type_def.parameters -*/
                {{ translator(parameter.type_ref) }}::toCpp(jniEnv, {{ parameter.jni.name }}){{ ", " if not loop.last }}
            /*>- endfor -*/
        );
        //> if type_def.return_type_ref:
        return ::pydjinni::release({{ translator(type_def.return_type_ref) }}::fromCpp(jniEnv, r));
        //> endif
    });
}

}
//> endif
//> endblock
