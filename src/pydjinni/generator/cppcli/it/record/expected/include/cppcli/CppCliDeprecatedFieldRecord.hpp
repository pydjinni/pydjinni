// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.pydjinni'
#pragma once
#include "deprecated_field_record.hpp"
#include "pydjinni/cppcli/Marshal.hpp"
namespace Test::Record::CppCli {
public ref class DeprecatedFieldRecord sealed  {
public:
    DeprecatedFieldRecord(int old, System::Nullable<int> older);

    [System::Obsolete("the field is old")]
    property int Old
    {
        int get();
    }
    /**
     * <summary>
     * <para>foo</para>
     * </summary>
     */
    [System::Obsolete("this is optional and old")]
    property System::Nullable<int> Older
    {
        System::Nullable<int> get();
    }
    System::String^ ToString() override;
internal:
    using CppType = ::test::record::DeprecatedFieldRecord;
    using CsType = DeprecatedFieldRecord^;

    static CppType ToCpp(CsType cs);
    static CsType FromCpp(const CppType& cpp);
private:
    int _old;
    System::Nullable<int> _older;
};
} // namespace Test::Record::CppCli
