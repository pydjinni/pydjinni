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
namespace {{ type_def.jni.name }} {
//> for error_code in type_def.error_codes:
{{ error_code.jni.name }}::{{ error_code.jni.name }}() = default;
{{ error_code.jni.name }}::~{{ error_code.jni.name }}() = default;

auto {{ error_code.jni.name }}::findClass() -> ::pydjinni::GlobalRef<jclass> {
    return ::pydjinni::jniFindClass("{{ type_def.jni.class_descriptor }}${{ error_code.java.name }}");
}

auto {{ error_code.jni.name }}::fromCpp(JNIEnv* jniEnv, const CppType& c) -> ::pydjinni::LocalRef<JniType> {
    const auto& data = ::pydjinni::JniClass<{{ error_code.jni.name }}>::get();
    auto r = ::pydjinni::LocalRef<JniType>{jniEnv->NewObject(
        data.clazz.get(), data.jconstructor
        //> for parameter in error_code.parameters:
        , ::pydjinni::get({{ parameter.jni.translator }}::fromCpp(jniEnv, c.{{ parameter.cpp.name }}))
        //> endfor
        , ::pydjinni::get(::pydjinni::jni::translator::String::fromCpp(jniEnv, c.what()))
    )};
    ::pydjinni::jniExceptionCheck(jniEnv);
    return r;
}

auto {{ error_code.jni.name }}::toCpp(JNIEnv* jniEnv, JniType j) -> CppType {
    ::pydjinni::JniLocalScope jscope(jniEnv, 5);
    assert(j != nullptr);
    const auto& data = ::pydjinni::JniClass<{{ error_code.jni.name }}>::get();
    return {{ error_code.jni.name }}::CppType {
    //> for parameter in error_code.parameters:
        {{ parameter.jni.translator }}::toCpp(jniEnv, ({{ parameter.jni.typename }})jniEnv->{{ parameter.jni.field_accessor }}(j, data.field_{{ parameter.jni.name }})),
    //> endfor
        ::pydjinni::jni::translator::String::toCpp(jniEnv, (jstring)jniEnv->CallObjectMethod(j, data.method_message))
    };
}
//> endfor
}
//> endblock
