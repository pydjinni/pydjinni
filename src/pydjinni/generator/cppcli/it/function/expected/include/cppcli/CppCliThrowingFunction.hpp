// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'function.pydjinni'
#pragma once
#include "throwing_function.hpp"
#include <functional>
#include <vcclr.h>
namespace Test::Function::CppCli {
public delegate void ThrowingFunction();
ref class _ThrowingFunctionDelegateCppProxy
{
public:
    _ThrowingFunctionDelegateCppProxy(const std::function<void()>& lambda) : _lambda(new std::function<void()>(lambda)) {}
    ~_ThrowingFunctionDelegateCppProxy();
    !_ThrowingFunctionDelegateCppProxy();

    void Invoke();
private:
    std::function<void()>* _lambda;
};

class _ThrowingFunctionDelegate {
public:
    using CppType = std::function<void()>;
    using CsType = ::Test::Function::CppCli::ThrowingFunction^;

    static CppType ToCpp(gcroot<CsType> delegate);
    static CsType FromCpp(const CppType& function);
};
} // namespace Test::Function::CppCli