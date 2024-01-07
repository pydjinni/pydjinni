// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'interface.djinni'
#pragma once
#include "calculator.hpp"
#include <memory>
#include "CppCliCalculator.hpp"
#include "pydjinni/cppcli/Marshal.hpp"
#include "CppCliPlatformInterface.hpp"

namespace Test::Interface::CppCli {
public ref class Calculator abstract {
public:
    static ::Test::Interface::CppCli::Calculator^ GetInstance();
    /**
     * <summary>
     * <para>adds up two values</para>
     * </summary>
     * <param name="a">the first value</param>
     * <param name="b">the second value</param>
     * <returns>
     * the sum of both values
     * </returns>
     */
    virtual char Add(char a, char b) abstract;
    virtual char GetPlatformValue(::Test::Interface::CppCli::PlatformInterface^ platform) abstract;
    virtual void NoParametersNoReturn() abstract;
    virtual void ThrowingException() abstract;
internal:
    using CppType = std::shared_ptr<::test::interface_test::Calculator>;
    using CppOptType = std::shared_ptr<::test::interface_test::Calculator>;
    using CsType = Calculator^;

    static CppType ToCpp(CsType cs);
    static CsType FromCppOpt(const CppOptType& cpp);
    static CsType FromCpp(const CppType& cpp) { return FromCppOpt(cpp); }
};
}  // namespace Test::Interface::CppCli