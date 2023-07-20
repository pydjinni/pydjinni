{% extends "base.jinja2" %}

{% block header %}
#pragma once

#include "pydjinni/jni/support.hpp"
#include {{ type_def.cpp.header | quote }}
{% endblock %}

{% block content %}
class {{ type_def.jni.name }} final : ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.name }}> {
public:
    using CppType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    using CppOptType = std::shared_ptr<{{ type_def.cpp.typename }}>;
    using JniType = {{ type_def.jni.typename.value }};
    using Boxed = {{ type_def.cpp.typename }};

    ~{{ type_def.jni.name }}();

    static CppType toCpp(JNIEnv* jniEnv, JniType j) { return ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get()._fromJava(jniEnv, j); }
    static ::pydjinni::LocalRef<JniType> fromCppOpt(JNIEnv* jniEnv, const CppOptType& c) { return {jniEnv, ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get()._toJava(jniEnv, c)}; }
    static ::pydjinni::LocalRef<JniType> fromCpp(JNIEnv* jniEnv, const CppType& c) { return fromCppOpt(jniEnv, c); }

private:
    {{ type_def.jni.name }}();
    friend ::pydjinni::JniClass<{{ type_def.jni.name }}>;
    friend ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.name }}>;


{% if 'java' in type_def.targets %}
    class JavaProxy final : ::pydjinni::JavaProxyHandle<JavaProxy>, public {{ type_def.cpp.typename }} {
    public:
        JavaProxy(JniType j);
        ~JavaProxy();

        {% for method in type_def.methods %}
        {{ method.cpp.type_spec }} {{ method.cpp.name }}(
        {%- for parameter in method.parameters -%}
            {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
        {%- endfor -%}
        ) {{ "const" if method.const }} override;
        {% endfor %}
    private:
        friend ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.translator }}>;
    };

    const ::pydjinni::GlobalRef<jclass> clazz { ::pydjinni::jniFindClass("{{ type_def.jni.class_descriptor }}") };
    {% for method in type_def.methods %}
    const jmethodID method_{{ method.jni.name }} { ::pydjinni::jniGetMethodID(clazz.get(), "{{ method.java.name }}", "{{ method.jni.type_signature }}") };
    {% endfor %}
{% endif %}
};
{% endblock %}
