// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'interface.djinni'
#pragma once
#include "deprecation_test.hpp"
#include <memory>
#include "pydjinni/cppcli/Marshal.hpp"

namespace Test::Interface::CppCli {
[Obsolete("testing class deprecation annotation")]
public ref class DeprecationTest abstract {
public:
    [Obsolete("testing method deprecation annotation")]
    virtual int DeprecationTestMethod() abstract;
internal:
    using CppType = std::shared_ptr<::test::interface_test::DeprecationTest>;
    using CppOptType = std::shared_ptr<::test::interface_test::DeprecationTest>;
    using CsType = DeprecationTest^;

    static CppType ToCpp(CsType cs);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp) { return FromCppOpt(cpp); }
};
}  // namespace Test::Interface::CppCli
