{% extends "base.jinja2" %}

{% block header %}
#include {{ type_def.jni.header | header }}
{% for dependency in type_def.dependencies %}
#include {{ dependency.jni.header | header }}
{% endfor %}
{% endblock %}

{% block content %}
{{ type_def.jni.name }}::{{ type_def.jni.name }}() = default;
{{ type_def.jni.name }}::~{{ type_def.jni.name }}() = default;

auto {{ type_def.jni.name }}::fromCpp(JNIEnv* jniEnv, const CppType& c) -> ::pydjinni::LocalRef<JniType> {
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.name }}>::get();
    auto r = ::pydjinni::LocalRef<JniType>{jniEnv->NewObject(
        data.clazz.get(), data.jconstructor,
        {% for field in type_def.fields %}
        ::pydjinni::get({{ field.type_ref.type_def.jni.translator }}::fromCpp(jniEnv, c.{{ field.cpp.name }})){{ "," if not loop.last }}
        {% endfor %}
    )};
    ::pydjinni::jniExceptionCheck(jniEnv);
    return r;
}

auto {{ type_def.jni.name }}::toCpp(JNIEnv* jniEnv, JniType j) -> CppType {
    ::pydjinni::JniLocalScope jscope(jniEnv, 5);
    assert(j != nullptr);
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.name }}>::get();
    return {
    {% for field in type_def.fields %}
        {{ field.type_ref.type_def.jni.translator }}::toCpp(jniEnv, jniEnv->{{ field.type_ref.type_def.jni.typename | get_field_accessor }}(j, data.field_{{ field.jni.name }})){{ "," if not loop.last }}
    {% endfor %}
    };
}
{% endblock %}
