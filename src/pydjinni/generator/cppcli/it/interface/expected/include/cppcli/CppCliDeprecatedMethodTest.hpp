// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'interface.pydjinni'
#pragma once
#include "deprecated_method_test.hpp"
#include "pydjinni/cppcli/Marshal.hpp"
namespace Test::Interface::CppCli {
public ref class DeprecatedMethodTest abstract {
public:
    [System::Obsolete("this method is deprecated but the type is not")]
    virtual bool DeprecatedTestMethod() abstract;
internal:
    using CppType = std::shared_ptr<::test::interface_test::DeprecatedMethodTest>;
    using CppOptType = std::shared_ptr<::test::interface_test::DeprecatedMethodTest>;
    using CsType = DeprecatedMethodTest^;

    static CppType ToCpp(CsType cs);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp) { return FromCppOpt(cpp); }
};
} // namespace Test::Interface::CppCli