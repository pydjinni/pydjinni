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

//> block content
class {{ type_def.jni.name }} final {
public:
    using CppType = {{ type_def.cpp.typename }};
    using JniType = {{ type_def.jni.typename.value }};

    using Boxed = {{ type_def.jni.name }};

    ~{{ type_def.jni.name }}();

    static CppType toCpp(JNIEnv* jniEnv, JniType j);
    static ::pydjinni::LocalRef<JniType> fromCpp(JNIEnv * jniEnv, const CppType& c);
private:
    {{ type_def.jni.name }}();
    friend ::pydjinni::JniClass<{{ type_def.jni.name }}>;

    const ::pydjinni::GlobalRef<jclass> clazz { ::pydjinni::jniFindClass("{{ type_def.jni.class_descriptor }}") };
    const jmethodID jconstructor { ::pydjinni::jniGetMethodID(clazz.get(), "<init>", "(
    /*>- for field in type_def.fields -*/
    {{ field.type_ref.type_def.jni.boxed_type_signature if field.type_ref.optional else field.type_ref.type_def.jni.type_signature }}
    /*>- endfor -*/
    )V") };
    //> for field in type_def.fields:
    const jfieldID field_{{ field.jni.name }} { ::pydjinni::jniGetFieldID(clazz.get(), "{{ field.java.name }}", "{{ field.type_ref.type_def.jni.boxed_type_signature if field.type_ref.optional else field.type_ref.type_def.jni.type_signature }}") };
    //> endfor
};
//> endblock
