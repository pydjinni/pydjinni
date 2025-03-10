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
{{ type_def.jni.name }}::{{ type_def.jni.name }}() = default;
{{ type_def.jni.name }}::~{{ type_def.jni.name }}() = default;

auto {{ type_def.jni.name }}::fromCpp(JNIEnv* jniEnv, const CppType& c) -> ::pydjinni::LocalRef<JniType> {
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.name }}>::get();
    //> if type_def.fields | map(attribute="deprecated") | any:
    PYDJINNI_DISABLE_DEPRECATED_WARNINGS
    //> endif
    auto r = ::pydjinni::LocalRef<JniType>(jniEnv->NewObject(
        data.clazz.get(), data.jconstructor
        /*> for field in type_def.fields */
        , ::pydjinni::get({{ field.jni.translator }}::fromCpp(jniEnv, c.{{ field.cpp.name }}))
        /*> endfor */
    ));
    //> if type_def.fields | map(attribute="deprecated") | any:
    PYDJINNI_ENABLE_WARNINGS
    //> endif
    ::pydjinni::jniExceptionCheck(jniEnv);
    return r;
}

auto {{ type_def.jni.name }}::toCpp(JNIEnv* jniEnv, JniType j) -> CppType {
    ::pydjinni::JniLocalScope jscope(jniEnv, 5);
    assert(j != nullptr);
    const auto& data = ::pydjinni::JniClass<{{ type_def.jni.name }}>::get();
    return {
    /*> for field in type_def.fields */
        {{ field.jni.translator }}::toCpp(jniEnv, ({{ field.jni.typename }})jniEnv->{{ field.jni.field_accessor }}(j, data.field_{{ field.jni.name }})){{ "," if not loop.last }}
    /*> endfor */
    };
}
//> endblock
