// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'function.djinni'
#pragma once
#include <functional>
#include <vcclr.h>

namespace Test::Function::CppCli {

ref class _FunctionVoidDelegateCppProxy
{
public:
    _FunctionVoidDelegateCppProxy(const std::function<void()>& lambda) : _lambda(new std::function<void()>(lambda)) {}
    ~_FunctionVoidDelegateCppProxy();
    !_FunctionVoidDelegateCppProxy();

    void Invoke();
private:
    std::function<void()>* _lambda;
};

class _FunctionVoidDelegate {
public:
    using CppType = std::function<void()>;
    using CsType = System::Action^;

    static CppType ToCpp(gcroot<CsType> delegate);
    static CsType FromCpp(const CppType& function);
};
}  // namespace Test::Function::CppCli
