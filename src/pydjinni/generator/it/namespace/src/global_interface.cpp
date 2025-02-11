#include "global_interface.hpp"

using namespace test::namespace_test;

test::namespace_test::something::namespaced::NamespacedRecord GlobalInterface::get_namespaced_record() noexcept
{
    return {
        {
            {
                5
            }
        }
    };
}

