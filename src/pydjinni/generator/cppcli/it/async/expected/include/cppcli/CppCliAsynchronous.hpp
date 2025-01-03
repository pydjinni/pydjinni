// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'async.pydjinni'
#pragma once
#include "asynchronous.hpp"
#include "CppCliAsynchronous.hpp"
#include "CppCliMultiplyCallback.hpp"
#include "CppCliNoParametersNoReturnCallback.hpp"
#include "CppCliThrowingCallback.hpp"
#include "pydjinni/coroutine/schedule.hpp"
#include "pydjinni/coroutine/task.hpp"
#include "pydjinni/cppcli/Marshal.hpp"
namespace Test::Async::CppCli {
public ref class Asynchronous abstract {
public:
    static System::Threading::Tasks::Task<::Test::Async::CppCli::Asynchronous^>^ GetInstance();
    virtual System::Threading::Tasks::Task<int>^ Add(int a, int b) abstract;
    virtual System::Threading::Tasks::Task^ NoParametersNoReturn() abstract;
    virtual System::Threading::Tasks::Task^ ThrowingException() abstract;
    virtual System::Threading::Tasks::Task<int>^ MultiplyCallback(::Test::Async::CppCli::MultiplyCallback^ callback) abstract;
    virtual System::Threading::Tasks::Task^ NoParametersNoReturnCallback(::Test::Async::CppCli::NoParametersNoReturnCallback^ callback) abstract;
    virtual System::Threading::Tasks::Task^ ThrowingCallback(::Test::Async::CppCli::ThrowingCallback^ callback) abstract;
internal:
    using CppType = std::shared_ptr<::test::async_test::Asynchronous>;
    using CppOptType = std::shared_ptr<::test::async_test::Asynchronous>;
    using CsType = Asynchronous^;

    static CppType ToCpp(CsType cs);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp) { return FromCppOpt(cpp); }
    ref class AddCallbackHandleProxy {
    public:
        AddCallbackHandleProxy(::pydjinni::coroutine::CallbackHandle<int32_t>& handle);
        void HandleCallback(System::Threading::Tasks::Task<int>^ task);
    private:
        ::pydjinni::coroutine::CallbackHandle<int32_t>* _handle;
    };
    ref class NoParametersNoReturnCallbackHandleProxy {
    public:
        NoParametersNoReturnCallbackHandleProxy(::pydjinni::coroutine::CallbackHandle<>& handle);
        void HandleCallback(System::Threading::Tasks::Task^ task);
    private:
        ::pydjinni::coroutine::CallbackHandle<>* _handle;
    };
    ref class ThrowingExceptionCallbackHandleProxy {
    public:
        ThrowingExceptionCallbackHandleProxy(::pydjinni::coroutine::CallbackHandle<>& handle);
        void HandleCallback(System::Threading::Tasks::Task^ task);
    private:
        ::pydjinni::coroutine::CallbackHandle<>* _handle;
    };
    ref class MultiplyCallbackCallbackHandleProxy {
    public:
        MultiplyCallbackCallbackHandleProxy(::pydjinni::coroutine::CallbackHandle<int32_t>& handle);
        void HandleCallback(System::Threading::Tasks::Task<int>^ task);
    private:
        ::pydjinni::coroutine::CallbackHandle<int32_t>* _handle;
    };
    ref class NoParametersNoReturnCallbackCallbackHandleProxy {
    public:
        NoParametersNoReturnCallbackCallbackHandleProxy(::pydjinni::coroutine::CallbackHandle<>& handle);
        void HandleCallback(System::Threading::Tasks::Task^ task);
    private:
        ::pydjinni::coroutine::CallbackHandle<>* _handle;
    };
    ref class ThrowingCallbackCallbackHandleProxy {
    public:
        ThrowingCallbackCallbackHandleProxy(::pydjinni::coroutine::CallbackHandle<>& handle);
        void HandleCallback(System::Threading::Tasks::Task^ task);
    private:
        ::pydjinni::coroutine::CallbackHandle<>* _handle;
    };
};
} // namespace Test::Async::CppCli
