// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'function.pydjinni'
#pragma once
#include "function_cpp_cppcli_java_objc_yaml_void_throws.hpp"
#include <functional>
#include <vcclr.h>
namespace Test::Function::CppCli {
ref class _FunctionCppCppcliJavaObjcYamlVoidThrowsDelegateCppProxy
{
public:
    _FunctionCppCppcliJavaObjcYamlVoidThrowsDelegateCppProxy(const std::function<void()>& lambda) : _lambda(new std::function<void()>(lambda)) {}
    ~_FunctionCppCppcliJavaObjcYamlVoidThrowsDelegateCppProxy();
    !_FunctionCppCppcliJavaObjcYamlVoidThrowsDelegateCppProxy();

    void Invoke();
private:
    std::function<void()>* _lambda;
};

class _FunctionCppCppcliJavaObjcYamlVoidThrowsDelegate {
public:
    using CppType = std::function<void()>;
    using CsType = System::Action^;

    static CppType ToCpp(gcroot<CsType> delegate);
    static CsType FromCpp(const CppType& function);
};
} // namespace Test::Function::CppCli
