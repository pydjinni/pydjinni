// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'error.pydjinni'
#pragma once
#include "CppCliFooError.hpp"
#include "throwing_callback.hpp"
namespace Test::Error::CppCli {
public ref class ThrowingCallback abstract {
public:
    virtual void ThrowingError() abstract;
internal:
    using CppType = std::shared_ptr<::test::error::ThrowingCallback>;
    using CppOptType = std::shared_ptr<::test::error::ThrowingCallback>;
    using CsType = ThrowingCallback^;

    static CppType ToCpp(CsType cs);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp) { return FromCppOpt(cpp); }
};
} // namespace Test::Error::CppCli