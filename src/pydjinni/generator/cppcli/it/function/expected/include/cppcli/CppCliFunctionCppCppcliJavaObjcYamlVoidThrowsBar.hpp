// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'function.pydjinni'
#pragma once
#include "CppCliBar.hpp"
#include "function_cpp_cppcli_java_objc_yaml_void_throws_bar.hpp"
#include <functional>
#include <vcclr.h>
namespace Test::Function::CppCli {
ref class _FunctionCppCppcliJavaObjcYamlVoidThrowsBarDelegateCppProxy
{
public:
    _FunctionCppCppcliJavaObjcYamlVoidThrowsBarDelegateCppProxy(const std::function<void()>& lambda) : _lambda(new std::function<void()>(lambda)) {}
    ~_FunctionCppCppcliJavaObjcYamlVoidThrowsBarDelegateCppProxy();
    !_FunctionCppCppcliJavaObjcYamlVoidThrowsBarDelegateCppProxy();

    void Invoke();
private:
    std::function<void()>* _lambda;
};

class _FunctionCppCppcliJavaObjcYamlVoidThrowsBarDelegate {
public:
    using CppType = std::function<void()>;
    using CppOptType = std::function<void()>;
    using CsType = System::Action^;

    static CppType ToCpp(gcroot<CsType> delegate);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp);
};
} // namespace Test::Function::CppCli
