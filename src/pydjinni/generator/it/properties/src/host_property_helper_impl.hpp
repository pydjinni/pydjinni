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

#pragma once
#include "host_properties.hpp"
#include "host_property_helper.hpp"
#include "readwrite_property_data.hpp"
#include "readonly_property_data.hpp"
#include "optional_property_data.hpp"
#include <memory>

namespace test::properties {

class HostPropertyHelperImpl: public HostPropertyHelper {
    std::shared_ptr<HostProperties> _properties;
    ::pydjinni::signals::connection _readwrite_property_change_connection;
    int64_t _readwrite_property_changed_value = 0;
    int _readwrite_property_callback_counter = 0;
    ::pydjinni::signals::connection _readonly_property_change_connection;
    std::string _readonly_property_changed_value = "unchanged";
    int _readonly_property_callback_counter = 0;
    ::pydjinni::signals::connection _optional_property_change_connection;
    std::optional<int64_t> _optional_property_changed_value = std::optional<int64_t>(0L);
    int _optional_property_callback_counter = 0;

public:
    HostPropertyHelperImpl(const std::shared_ptr<HostProperties>& properties) noexcept;
    ReadwritePropertyData readwrite_property_data() noexcept override;
    void modify_host_readwrite_property() noexcept override;
    ReadonlyPropertyData readonly_property_data() noexcept override;
    OptionalPropertyData optional_property_data() noexcept override;
};

} // namespace test::properties
