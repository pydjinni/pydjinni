#include "main_interface.hpp"

using namespace test::external_types;


bool MainInterface::use_external_types(
        ::test::exported_types::foo::EnumType enum_param, ::test::exported_types::FlagsType flags_param,
        const test::exported_types::RecordType &record_param,
        const std::function<bool()> &function_param) noexcept {
    return function_param();
}
