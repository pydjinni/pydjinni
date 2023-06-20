{% extends "base.jinja2" %}

{% block header %}
#pragma once

#include "pydjinni/jni/support.hpp"
#include {{ type_def.cpp.header | header }}
{% endblock %}

{% block content %}
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

    const ::pydjinni::GlobalRef<jclass> clazz { ::pydjinni::jniFindClass("{{ type_def.jni.type_signature }}") };
    const jmethodID jconstructor { ::pydjinni::jniGetMethodID(clazz.get(), "<init>", "(
    {%- for field in type_def.fields -%}
    {{ field.type_ref.type_def.jni.type_signature }}
    {%- endfor -%}
    )V") };
    {% for field in type_def.fields %}
    const jfieldID field_{{ field.jni.name }} { ::pydjinni::jniGetFieldID(clazz.get(), "{{ field.java.name }}", "{{ field.type_ref.type_def.jni.type_signature }}") };
    {% endfor %}
};
{% endblock %}
