{% extends "base.jinja2" %}
{% from "macros.jinja2" import translator %}

{% block header %}
#include {{ type_def.jni.header | quote }}
{% for header in type_def.dependencies | headers('jni') -%}
#include {{ header }}
{% endfor %}
{% endblock %}

{% macro return_type(method) %}
{{ method.return_type_ref.type_def.jni.typename.value if method.return_type_ref else "void" }}
{% endmacro %}

{% block content %}
{{ type_def.jni.name }}::{{ type_def.jni.name }}() : ::pydjinni::JniInterface<{{ type_def.cpp.typename }}, {{ type_def.jni.name }}>("{{ type_def.jni.class_descriptor }}$CppProxy") {}
{{ type_def.jni.name }}::~{{ type_def.jni.name }}() = default;

{% if 'java' in type_def.targets %}
{{ type_def.jni.name }}::JavaProxy::JavaProxy(JniType j) : Handle(::pydjinni::jniGetThreadEnv(), j) {}
{{ type_def.jni.name }}::JavaProxy::~JavaProxy() = default;

{% for method in type_def.methods %}
{{ method.cpp.type_spec }} {{ type_def.jni.name }}::JavaProxy::{{ method.cpp.name }}(
{%- for parameter in method.parameters -%}
    {{ parameter.cpp.type_spec }} {{ parameter.cpp.name ~ (", " if not loop.last) }}
{%- endfor -%}
) {{ "const" if method.const }} {
    auto jniEnv = ::pydjinni::jniGetThreadEnv();
    ::pydjinni::JniLocalScope jscope(jniEnv, 10);
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.translator }}>::get();
    {{ "auto jret = " if method.return_type_ref }} jniEnv->{{ method.jni.routine_name }}(Handle::get().get(), data.method_{{ method.java.name }}
    {%- for parameter in method.parameters -%}
        , ::pydjinni::get({{ translator(parameter.type_ref) }}::fromCpp(jniEnv, {{ parameter.cpp.name }}))
    {%- endfor -%}
    );
    ::pydjinni::jniExceptionCheck(jniEnv);
    {% if method.return_type_ref %}
    return {{ translator(method.return_type_ref) }}::toCpp(jniEnv, jret);
    {% endif %}
}
{% endfor %}
{% endif %}

{% if 'cpp' in type_def.targets %}
CJNIEXPORT void JNICALL {{ type_def.jni.jni_prefix }}_nativeDestroy(JNIEnv* jniEnv, jobject /*this*/, jlong nativeRef)
{
    ::pydjinni::translate_exceptions(jniEnv, [&](){
        delete reinterpret_cast<::pydjinni::CppProxyHandle<{{ type_def.cpp.typename }}>*>(nativeRef);
    });
}

{% for method in type_def.methods %}
CJNIEXPORT {{ return_type(method) }} JNICALL {{ type_def.jni.jni_prefix }}_00024CppProxy_{{ "native_1" if not method.static }}{{ method.jni.jni_name }}(JNIEnv* jniEnv, jobject /*this*/{{ ", jlong nativeRef" if not method.static }}
    {%- for parameter in method.parameters -%}
    , {{ parameter.type_ref.type_def.jni.typename.value }} {{ parameter.jni.name }}
    {%- endfor -%}
    ) {
    {{ "return" if method.return_type_ref }} ::pydjinni::translate_exceptions(jniEnv, [&](){
        {% if method.static %}
        {{ "auto r = " if method.return_type_ref }}{{ type_def.cpp.typename }}::{{ method.cpp.name }}(
        {%- else -%}
        const auto& ref = ::pydjinni::objectFromHandleAddress<{{ type_def.cpp.typename }}>(nativeRef);
        {{ "auto r = " if method.return_type_ref }}ref->{{ method.cpp.name }}(
        {%- endif -%}
        {%- for parameter in method.parameters -%}
        {{ translator(parameter.type_ref) }}::toCpp(jniEnv, {{ parameter.jni.name }}){{ ", " if not loop.last }}
        {%- endfor -%}
        );
        {% if method.return_type_ref %}
        return ::pydjinni::release({{ translator(method.return_type_ref) }}::fromCpp(jniEnv, r));
        {% endif %}
    });
}
{% endfor %}
{% endif %}
{% endblock %}
