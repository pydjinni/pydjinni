// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'function.pydjinni'
#pragma once
#include "function_cpp_cppcli_java_objc_yaml_string_bool.hpp"
#include "pydjinni/cppcli/Marshal.hpp"
#include <functional>
#include <vcclr.h>
namespace Test::Function::CppCli {
ref class _FunctionCppCppcliJavaObjcYamlStringBoolDelegateCppProxy
{
public:
    _FunctionCppCppcliJavaObjcYamlStringBoolDelegateCppProxy(const std::function<bool(std::string)>& lambda) : _lambda(new std::function<bool(std::string)>(lambda)) {}
    ~_FunctionCppCppcliJavaObjcYamlStringBoolDelegateCppProxy();
    !_FunctionCppCppcliJavaObjcYamlStringBoolDelegateCppProxy();

    bool Invoke(System::String^ param);
private:
    std::function<bool(std::string)>* _lambda;
};

class _FunctionCppCppcliJavaObjcYamlStringBoolDelegate {
public:
    using CppType = std::function<bool(std::string)>;
    using CppOptType = std::function<bool(std::string)>;
    using CsType = System::Func<System::String^, bool>^;

    static CppType ToCpp(gcroot<CsType> delegate);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp);
};
} // namespace Test::Function::CppCli
