#include "base_record_base.hpp"

namespace test::record {
struct BaseRecord final : public BaseRecordBase {
    using BaseRecordBase::BaseRecordBase;

    BaseRecord()
    : BaseRecordBase(42)
    {}
};
}

