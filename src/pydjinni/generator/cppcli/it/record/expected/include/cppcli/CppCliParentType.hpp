// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
#pragma once
#include "CppCliNestedType.hpp"
#include "parent_type.hpp"
namespace Test::Record::CppCli {
public ref class ParentType sealed  {
public:
    ParentType(::Test::Record::CppCli::NestedType^ nested);

    property ::Test::Record::CppCli::NestedType^ Nested
    {
        ::Test::Record::CppCli::NestedType^ get();
    }
    System::String^ ToString() override;
internal:
    using CppType = ::test::record::ParentType;
    using CsType = ParentType^;

    static CppType ToCpp(CsType cs);
    static CsType FromCpp(const CppType& cpp);
private:
    ::Test::Record::CppCli::NestedType^ _nested;
};
} // namespace Test::Record::CppCli
