// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'record.djinni'
#pragma once
#include "base_record.hpp"
#include "pydjinni/cppcli/Marshal.hpp"

namespace Test::Record::CppCli {
ref class BaseRecord;

[System::Serializable]
public ref class BaseRecordBase abstract  {
public:
    BaseRecordBase(int value);

    property int Value
    {
        int get();
    }
internal:
    using CppType = ::test::record::BaseRecord;
    using CsType = BaseRecord^;

    static CppType ToCpp(CsType cs);
    static CsType FromCpp(const CppType& cpp);
private:
    int _value;
};
}  // namespace Test::Record::CppCli
