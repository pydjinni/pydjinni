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
class {{ type_def.jni.name }} final : ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.name }}> {
public:
    using CppType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    using CppOptType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    using JniType = {{ type_def.jni.typename }};
    using Boxed = {{ type_def.jni.translator }};

    ~{{ type_def.jni.name }}();

    static CppType toCpp(JNIEnv* jniEnv, JniType j) { return ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get()._fromJava(jniEnv, j); }
    static ::pydjinni::LocalRef<JniType> fromCppOpt(JNIEnv* jniEnv, const CppOptType& c) { return {jniEnv, ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get()._toJava(jniEnv, c)}; }
    static ::pydjinni::LocalRef<JniType> fromCpp(JNIEnv* jniEnv, const CppType& c) { return fromCppOpt(jniEnv, c); }

private:
    {{ type_def.jni.name }}();
    friend ::pydjinni::JniClass<{{ type_def.jni.name }}>;
    friend ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.name }}>;


//> if 'java' in type_def.targets:
    class JavaProxy final : ::pydjinni::JavaProxyHandle<JavaProxy>, public {{ type_def.cpp.typename }} {
    public:
        JavaProxy(JniType j);
        ~JavaProxy();

        //> for method in type_def.methods:
        {{ method.cpp.prefix_specifiers(implementation=True) ~ method.cpp.type_spec }} {{ method.cpp.name }}(
        /*>- for parameter in method.parameters -*/
            {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
        ){{ method.cpp.postfix_specifiers(implementation=True) }} override;
        //> endfor
    private:
        friend ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.translator }}>;
    };

    const ::pydjinni::GlobalRef<jclass> clazz { ::pydjinni::jniFindClass("{{ type_def.jni.class_descriptor }}") };
    //> for method in type_def.methods:
    const jmethodID method_{{ method.jni.name }} { ::pydjinni::jniGetMethodID(clazz.get(), "{{ method.java.name }}", "{{ method.jni.type_signature }}") };
    //> endfor
//> endif
};
//> endblock
