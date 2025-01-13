#pragma once
#include <jni.h>
#include "support.hpp"
#include "marshal.hpp"

namespace pydjinni::jni {

class Jni {
    JNIEnv* env;

public:
    explicit Jni(JNIEnv* env) : env(env) {}
    Jni() : env(::pydjinni::jniGetThreadEnv()) {}

    template<typename Error>
    void Throw(const Error::CppType& e) const noexcept {
        env->Throw((jthrowable)get(Error::fromCpp(env, e)));
    }

    void Throw(const jni_exception & e) const noexcept {
        e.set_as_pending(env);
    }

    void Throw(const std::exception& e) const noexcept {
        env->ThrowNew(env->FindClass("java/lang/RuntimeException"), e.what());
    }

    template<typename Translator>
    Translator::JniType Return(const auto& value) const {
        return release(Translator::fromCpp(env, value));
    }

    class CompletableFuture {
        JNIEnv* env;
        jobject ref;
        jobject globalRef;
        explicit CompletableFuture(JNIEnv* env) : env(env) {
            auto clazz = CompletableFuture::clazz(env);
            auto init = env->GetMethodID(clazz, "<init>", "()V");
            ref = env->NewObject(clazz, init);
            globalRef = env->NewGlobalRef(ref);
        }
        [[nodiscard]] static jclass clazz(JNIEnv* env) {
            return env->FindClass("java/util/concurrent/CompletableFuture");
        }

        [[nodiscard]] static jmethodID complete(JNIEnv* env) {
            return env->GetMethodID(clazz(env), "complete", "(Ljava/lang/Object;)Z");
        }

        [[nodiscard]] static jmethodID completeExceptionally(JNIEnv* env) {
            return env->GetMethodID(clazz(env), "completeExceptionally", "(Ljava/lang/Throwable;)Z");
        }
        friend class Jni;
    public:
        class CompletionHandler {
            jobject ref;
            explicit CompletionHandler(jobject globalRef) : ref(globalRef) {}
            friend class CompletableFuture;
        public:
            void Complete() const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref, complete(localEnv), nullptr);
                localEnv->DeleteGlobalRef(ref);
            }
            template<typename Translator>
            void Complete(Translator::CppType value) const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref, complete(localEnv), ::pydjinni::release(Translator::Boxed::fromCpp(localEnv, value)));
                localEnv->DeleteGlobalRef(ref);

            }
            void CompleteExceptionally(const jni_exception& e) const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref, completeExceptionally(localEnv), e.java_exception());
                localEnv->DeleteGlobalRef(ref);
            }
            void CompleteExceptionally(const std::exception& e) const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref, completeExceptionally(localEnv), ::pydjinni::jniNewThrowable(localEnv, ::pydjinni::release(::pydjinni::jni::translator::String::fromCpp(localEnv, e.what()))));
                localEnv->DeleteGlobalRef(ref);
            }
            template<typename Error>
            void CompleteExceptionally(const Error::CppType& e) const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref, completeExceptionally(localEnv), ::pydjinni::get(Error::fromCpp(localEnv, e)));
                localEnv->DeleteGlobalRef(ref);
            }
        };

        [[nodiscard]] CompletionHandler Handle() const {
            return CompletionHandler{globalRef};
        }

        [[nodiscard]] jobject Return() const {
            return ref;
        }
    };

    template<typename JavaObject>
    JavaObject New() const {
        return JavaObject(env);
    }

};

}
