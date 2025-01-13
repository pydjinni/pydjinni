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
class {{ error_code.jni.name }} final {
public:
    using CppType = {{ type_def.cpp.typename }}::{{ error_code.cpp.name }};
    using JniType = {{ error_code.jni.typename.value }};

    using Boxed = {{ error_code.jni.name }};

    ~{{ error_code.jni.name }}();

    static ::pydjinni::GlobalRef<jclass> findClass();
    static CppType toCpp(JNIEnv* jniEnv, JniType j);
    static ::pydjinni::LocalRef<JniType> fromCpp(JNIEnv * jniEnv, const CppType& c);
private:
    {{ error_code.jni.name }}();
    friend ::pydjinni::JniClass<{{ error_code.jni.name }}>;

    const ::pydjinni::GlobalRef<jclass> clazz { findClass() };
    const jmethodID jconstructor { ::pydjinni::jniGetMethodID(clazz.get(), "<init>", "(
    /*>- for parameter in error_code.parameters -*/
    {{ parameter.type_ref.type_def.jni.boxed_type_signature if parameter.type_ref.optional else parameter.type_ref.type_def.jni.type_signature }}
    /*>- endfor -*/
    Ljava/lang/String;)V") };
    /*> for parameter in error_code.parameters */
    const jfieldID field_{{ parameter.jni.name }} { ::pydjinni::jniGetFieldID(clazz.get(), "{{ parameter.java.name }}", "{{ parameter.type_ref.type_def.jni.boxed_type_signature if parameter.type_ref.optional else parameter.type_ref.type_def.jni.type_signature }}") };
    /*> endfor */
    const jmethodID method_message { ::pydjinni::jniGetMethodID(clazz.get(), "getMessage", "()Ljava/lang/String;") };
};
//> endfor
}
//> endblock
