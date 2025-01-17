// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
#pragma once
#include "optional_types.hpp"
#include "pydjinni/cppcli/Marshal.hpp"
namespace Test::Record::CppCli {
public ref class OptionalTypes sealed  {
public:
    OptionalTypes(System::Nullable<int> intOptional, System::String^ stringOptional);

    property System::Nullable<int> IntOptional
    {
        System::Nullable<int> get();
    }
    property System::String^ StringOptional
    {
        System::String^ get();
    }
    System::String^ ToString() override;
internal:
    using CppType = ::test::record::OptionalTypes;
    using CsType = OptionalTypes^;

    static CppType ToCpp(CsType cs);
    static CsType FromCpp(const CppType& cpp);
private:
    System::Nullable<int> _intOptional;
    System::String^ _stringOptional;
};
} // namespace Test::Record::CppCli
