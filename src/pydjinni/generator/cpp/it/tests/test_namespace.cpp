// Copyright 2025 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "catch2/catch_test_macros.hpp"
#include <catch2/matchers/catch_matchers_string.hpp>
#include "global_interface.hpp"
#include "something/namespaced/namespaced_interface.hpp"

TEST_CASE("Cpp.NamespaceTest") {
    WHEN("using the global interface") {
        const auto result = ::test::namespace_test::GlobalInterface::get_namespaced_record();
        THEN("the namespaced record should be returned") {
            REQUIRE(result == ::test::namespace_test::something::namespaced::NamespacedRecord { { { 5 } } });
        }
    }
    WHEN("using the namespaced interface") {
        const auto result = ::test::namespace_test::something::namespaced::NamespacedInterface::get_global_record();
        THEN("the global record should be returned") {
            REQUIRE(result == ::test::namespace_test::GlobalRecord { { 5 } });
        }
    }
}
