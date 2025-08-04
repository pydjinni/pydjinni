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
#include "cpp_properties.hpp"
#include "host_properties.hpp"
#include "host_property_helper.hpp"

TEST_CASE("PropertiesTest") {
    GIVEN("a CppProperties interface instance") {
        auto properties = ::test::properties::CppProperties::get_instance();
        WHEN("setting a property") {
            properties->set_readwrite_property(42L);
            THEN("the the set value should be returned") {
                REQUIRE(properties->get_readwrite_property() == 42L);
            }
        }
        WHEN("registering a callback on property change") {
            int64_t callback_value = 0L;
            auto connection = properties->on_readwrite_property_changed([&callback_value](int64_t value) {
                callback_value = value;
            });
            AND_WHEN("setting a value for the property") {
                properties->set_readwrite_property(42L);
                THEN("the callback should be triggered") {
                    REQUIRE(callback_value == 42L);
                }
            }
            AND_WHEN("deregistering the callback again") {
                connection.disconnect();
                AND_WHEN("setting a value for the property") {
                    properties->set_readwrite_property(42L);
                    THEN("the callback should not be triggered") {
                        REQUIRE(callback_value == 0);
                        AND_THEN("the correct value should be set anyways") {
                            const auto value = properties->get_readwrite_property();
                            REQUIRE(value == 42L);
                        }
                    }
                }
            }
            AND_WHEN("deleting the CppProperties instance") {
                properties.reset();
                THEN("calling disconnect on the signal should do nothing and not fail") {
                    connection.disconnect();
                }
            }
        }
        WHEN("registering a scoped connection") {
            bool callback_called = false;
            {
                const auto connection = properties->on_readwrite_property_changed([&callback_called](auto value){
                    callback_called = true;
                });
            }
            THEN("the signal should not be triggered after the connection went out of scope") {
                properties->set_readwrite_property(42L);
                REQUIRE(callback_called == false);
            }
        }
        WHEN("changing a readonly property through a side-effect") {
            std::string callback_value = "uncalled";
            const auto connection = properties->on_readonly_property_changed([&callback_value](auto value) {
                callback_value = value;
            });
            properties->change_readonly_property();
            THEN("the changed value should be returned by the property") {
                REQUIRE(properties->get_readonly_property() == "changed");
            }
            THEN("the callback should have been triggered") {
                REQUIRE(callback_value == "changed");
            }
        }
        WHEN("setting a listener on an optional property") {
            std::optional<int64_t> callback_value = 0L;
            const auto connection = properties->on_optional_property_changed([&callback_value](auto value){
                callback_value = value;
            });
            AND_WHEN("setting the optional property to a non-null value") {
                properties->set_optional_property(std::optional<int64_t>{42L});
                THEN("the value should be returned by the getter") {
                    REQUIRE(properties->get_optional_property() == 42L);
                }
                THEN("the callback should have been triggered") {
                    REQUIRE(callback_value == 42L);
                }
            }
            AND_WHEN("setting the optional property to a nullptr") {
                properties->set_optional_property(std::nullopt);
                THEN("the value should be returned by the getter") {
                    REQUIRE(properties->get_optional_property() == std::nullopt);
                }
                THEN("the callback should have been triggered") {
                    REQUIRE(callback_value == std::nullopt);
                }
            }
        }
        
    }
    GIVEN("a host properties implementation and instance") {
        struct HostPropertiesImpl : public ::test::properties::HostProperties {
            void change_readonly_property() noexcept override {
                set_readonly_property("changed");
            }
        };
        const auto host_properties = std::make_shared<HostPropertiesImpl>();
        AND_GIVEN("a host properties helper instance") {
            const auto helper = ::test::properties::HostPropertyHelper::setup(host_properties);
            WHEN("changing the host readwrite property") {
                host_properties->set_readwrite_property(42L);
                THEN("the value should be set and the helper should have been notified once") {
                    const auto result = helper->readwrite_property_data();
                    REQUIRE(result.change_counter == 1);
                    REQUIRE(result.callback_value == 42L);
                    REQUIRE(result.read_value == 42L);
                }
            }
            WHEN("changing the host readolny property") {
                host_properties->change_readonly_property();
                THEN("the value should be set and the helper should have been notified once") {
                    const auto result = helper->readonly_property_data();
                    REQUIRE(result.change_counter == 1);
                    REQUIRE(result.callback_value == "changed");
                    REQUIRE(result.read_value == "changed");
                }
            }
        }
        AND_GIVEN("a notification listener to readwrite property changes") {
            int64_t callback_value = 0L;
            const auto connection = host_properties->on_readwrite_property_changed([&](int64_t value){
                callback_value = value;
            });
            AND_GIVEN("a host properties helper instance") {
                const auto helper = ::test::properties::HostPropertyHelper::setup(host_properties);
                WHEN("instructing the helper to change a host property") {
                    helper->modify_host_readwrite_property();
                    THEN("the host property should be updated") {
                        REQUIRE(host_properties->get_readwrite_property() == 2L);
                    }
                    THEN("the callback should have been triggered") {
                        REQUIRE(callback_value == 2L);
                    }
                }
            }
        }
    }
}
