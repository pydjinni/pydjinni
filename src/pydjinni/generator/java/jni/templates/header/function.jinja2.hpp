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

class {{ type_def.jni.wrapper }} {
public:
    virtual {{ type_def.cpp.type_spec }} invoke(
        /*>- for parameter in type_def.parameters -*/
            {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
    ){{ " noexcept" if type_def.cpp.noexcept }} = 0;
};

class {{ type_def.jni.name }} final : ::pydjinni::JniInterface<{{ type_def.jni.wrapper }}, {{ type_def.jni.name }}> {
public:
    using CppType = {{ type_def.cpp.typename }};
    using CppOptType = {{ type_def.cpp.typename }};
    using JniType = {{ type_def.jni.typename }};
    using Boxed = {{ type_def.jni.translator }};

    ~{{ type_def.jni.name }}();

    static {{ type_def.cpp.typename }} toCpp(JNIEnv* jniEnv, JniType j);
    static ::pydjinni::LocalRef<JniType> fromCppOpt(JNIEnv* jniEnv, const {{ type_def.cpp.typename }}& c);
    static ::pydjinni::LocalRef<JniType> fromCpp(JNIEnv* jniEnv, const {{ type_def.cpp.typename }}& c);

private:
    {{ type_def.jni.name }}();
    friend ::pydjinni::JniClass<{{ type_def.jni.name }}>;
    friend ::pydjinni::JniInterface<{{ type_def.jni.wrapper }}, {{ type_def.jni.name }}>;

    class CppProxy final : public {{ type_def.jni.wrapper }} {
    public:
        CppProxy(const {{ type_def.cpp.typename }}& lambda) : _lambda(lambda) {};

        {{ type_def.cpp.type_spec }} invoke(
        /*>- for parameter in type_def.parameters -*/
            {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
        ){{ " noexcept" if type_def.cpp.noexcept }} override {
            {{ "return " if type_def.return_type_ref }}_lambda(
                /*>- for parameter in type_def.parameters -*/
                    {{ parameter.cpp.name ~ (", " if not loop.last) }}
                /*>- endfor -*/
            );
        }
    private:
        {{ type_def.cpp.typename }} _lambda;
    };


//> if 'java' in type_def.targets:
    class JavaProxy final : ::pydjinni::JavaProxyHandle<JavaProxy>, public {{ type_def.jni.wrapper }} {
    public:
        JavaProxy(JniType j);
        ~JavaProxy();

        {{ type_def.cpp.type_spec }} invoke(
        /*>- for parameter in type_def.parameters -*/
            {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
        /*>- endfor -*/
        ){{ " noexcept" if type_def.cpp.noexcept }} override;
    private:
        friend ::pydjinni::JniInterface<{{ type_def.jni.wrapper }}, {{ type_def.jni.translator }}>;
    };

    const ::pydjinni::GlobalRef<jclass> clazz { ::pydjinni::jniFindClass("{{ type_def.jni.class_descriptor }}") };

    const jmethodID method_invoke { ::pydjinni::jniGetMethodID(clazz.get(), "invoke", "{{ type_def.jni.type_signature }}") };

//> endif
};
//> endblock
