#include "something/namespaced/namespaced_interface.hpp"

using namespace test::namespace_test::something::namespaced;

test::namespace_test::GlobalRecord NamespacedInterface::get_global_record() noexcept
{
    return {
        {
            5
        }
    };
}

