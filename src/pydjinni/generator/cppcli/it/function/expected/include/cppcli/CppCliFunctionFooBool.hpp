// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'function.pydjinni'
#pragma once
#include "CppCliFoo.hpp"
#include "function_foo_bool.hpp"
#include "pydjinni/cppcli/Marshal.hpp"
#include <functional>
#include <vcclr.h>
namespace Test::Function::CppCli {
ref class _FunctionFooBoolDelegateCppProxy
{
public:
    _FunctionFooBoolDelegateCppProxy(const std::function<bool(::test::function::Foo)>& lambda) : _lambda(new std::function<bool(::test::function::Foo)>(lambda)) {}
    ~_FunctionFooBoolDelegateCppProxy();
    !_FunctionFooBoolDelegateCppProxy();

    bool Invoke(::Test::Function::CppCli::Foo^ param);
private:
    std::function<bool(::test::function::Foo)>* _lambda;
};

class _FunctionFooBoolDelegate {
public:
    using CppType = std::function<bool(::test::function::Foo)>;
    using CsType = System::Func<::Test::Function::CppCli::Foo^, bool>^;

    static CppType ToCpp(gcroot<CsType> delegate);
    static CsType FromCpp(const CppType& function);
};
} // namespace Test::Function::CppCli
