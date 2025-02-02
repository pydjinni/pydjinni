#pragma once
#include <jni.h>
#include "support.hpp"
#include "marshal.hpp"
#if __has_include("pydjinni/coroutine/completion.hpp")
#define ASYNC_SUPPORTED
#include "pydjinni/coroutine/completion.hpp"
#endif

namespace pydjinni::jni {

class Jni {
public:
    JNIEnv* const env;
    explicit Jni(JNIEnv* env) : env(env) {}
    Jni() : env(::pydjinni::jniGetThreadEnv()) {}

    [[nodiscard]] ::pydjinni::LocalRef<jthrowable> ExceptionOccurred() const {
        if(auto throwable = ::pydjinni::LocalRef<jthrowable>{env, env->ExceptionOccurred()}) {
            env->ExceptionClear();
            return throwable;
        }
        return {};
    }

    template<typename Translator>
    [[nodiscard]] jboolean IsInstanceOf(const jthrowable& obj) const {
        return env->IsInstanceOf(obj, Translator::findClass().get());
    }

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

    void Terminate(const ::pydjinni::LocalRef<jthrowable>& e) const {
        try {
            throw ::pydjinni::jni_exception { env, e.get() };
        } catch (const ::pydjinni::jni_exception&) {
            std::terminate();
        }
    }

    class CompletableFuture {
        JNIEnv* const env;
        jobject ref;
        explicit CompletableFuture(JNIEnv* env) : env(env) {
            auto clazz = CompletableFuture::clazz(env);
            auto init = env->GetMethodID(clazz, "<init>", "()V");
            ref = env->NewObject(clazz, init);
        }
        CompletableFuture(JNIEnv* env, const jobject& ref) : env(env), ref(ref) {}
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
            GlobalRef<jobject> ref;
            explicit CompletionHandler(const GlobalRef<jobject>& globalRef) : ref(globalRef) {}
            friend class CompletableFuture;
        public:
            void Complete() const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref.get(), complete(localEnv), nullptr);
            }
            template<typename Translator>
            void Complete(Translator::CppType value) const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref.get(), complete(localEnv), ::pydjinni::release(Translator::Boxed::fromCpp(localEnv, value)));

            }
            void CompleteExceptionally(const jni_exception& e) const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref.get(), completeExceptionally(localEnv), e.java_exception());
            }
            void CompleteExceptionally(const std::exception& e) const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref.get(), completeExceptionally(localEnv), ::pydjinni::jniNewThrowable(localEnv, ::pydjinni::release(::pydjinni::jni::translator::String::fromCpp(localEnv, e.what()))));
            }
            template<typename Error>
            void CompleteExceptionally(const Error::CppType& e) const {
                const auto localEnv = ::pydjinni::jniGetThreadEnv();
                localEnv->CallBooleanMethod(ref.get(), completeExceptionally(localEnv), ::pydjinni::get(Error::fromCpp(localEnv, e)));
            }
        };

        [[nodiscard]] CompletionHandler Handle() const {
            return CompletionHandler{GlobalRef<jobject>(env, ref)};
        }

#ifdef ASYNC_SUPPORTED
        void WhenComplete(const ::pydjinni::jni::CompletionHandler& handler) {
            auto clazz = CompletableFuture::clazz(env);
            auto completionMethod = ::pydjinni::jniGetMethodID(clazz, "whenComplete", "(Ljava/util/function/BiConsumer;)Ljava/util/concurrent/CompletableFuture;");
            env->CallObjectMethod(ref, completionMethod, ::pydjinni::release(::pydjinni::jni::NativeCompletion::fromCpp(env, handler)));
            ::pydjinni::jniExceptionCheck(env);
        }
#endif
        [[nodiscard]] jobject Return() const {
            return ref;
        }
    };

    class Throwable {
        JNIEnv* const env;
        jthrowable ref;
        Throwable(JNIEnv* env, const jthrowable& ref)
        : env(env)
        , ref(ref) {}
        friend class Jni;
    public:
        [[nodiscard]] jthrowable GetCause() const {
            jmethodID getCause = env->GetMethodID(::pydjinni::jniFindClass("java/lang/Throwable").get(), "getCause", "()Ljava/lang/Throwable;");
            const auto cause = (jthrowable)env->CallObjectMethod(ref, getCause);
            ::pydjinni::jniExceptionCheck(env);
            return cause;
        }
    };

    template<typename JavaObject>
    JavaObject New() const {
        return JavaObject(env);
    }

    template<typename JavaObject>
    JavaObject Get(const auto& ref) const {
        return JavaObject(env, ref);
    }

};

class ScopedJni : public Jni {
    ::pydjinni::JniLocalScope jscope;
public:
    explicit ScopedJni(jint capacity = 10): Jni(), jscope(env, capacity) {}
};

}
