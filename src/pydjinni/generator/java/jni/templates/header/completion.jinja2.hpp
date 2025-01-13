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
// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni
#pragma once
#include "pydjinni/jni/support.hpp"

namespace {{ namespace }} {

    struct CompletionHandler {
        std::function<void(jobject)> onSuccess;
        std::function<void(jthrowable)> onError;
    };

    class NativeCompletion final : ::pydjinni::JniInterface<CompletionHandler, NativeCompletion> {
    public:

        ~NativeCompletion() = default;

        static ::pydjinni::LocalRef<jobject> fromCpp(JNIEnv* jniEnv, const CompletionHandler& c) {
            return {jniEnv, ::pydjinni::JniClass<NativeCompletion>::get()._toJava(jniEnv, std::make_shared<CompletionHandler>(c))};
        }
    private:
        NativeCompletion() : ::pydjinni::JniInterface<CompletionHandler, NativeCompletion>("{{ java_type_signature }}") {};

        friend ::pydjinni::JniClass<NativeCompletion>;
        friend ::pydjinni::JniInterface<CompletionHandler, NativeCompletion>;
    };
}
