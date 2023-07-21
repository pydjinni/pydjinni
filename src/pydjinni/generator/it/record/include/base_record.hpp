#include "base_record_base.hpp"

namespace test::record {
struct BaseRecord final : public BaseRecordBase {
    BaseRecord()
    : BaseRecordBase(42)
    {}

    BaseRecord(int32_t value_)
    : BaseRecordBase(value_)
    {}
};
}

