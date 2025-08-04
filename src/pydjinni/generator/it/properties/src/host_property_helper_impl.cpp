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

#include "host_property_helper_impl.hpp"
#include <stdexcept>

namespace test::properties {

std::shared_ptr<HostPropertyHelper> HostPropertyHelper::setup(const std::shared_ptr<HostProperties>& properties) noexcept {
    return std::make_shared<HostPropertyHelperImpl>(properties);
}

HostPropertyHelperImpl::HostPropertyHelperImpl(const std::shared_ptr<HostProperties>& properties) noexcept
 : _properties(std::move(properties))
 , _readwrite_property_change_connection(_properties->on_readwrite_property_changed([&](auto value){
    _readwrite_property_changed_value = value;
    _readwrite_property_callback_counter++;
 }))
 , _readonly_property_change_connection(_properties->on_readonly_property_changed([&](auto value){
    _readonly_property_changed_value = value;
    _readonly_property_callback_counter++;
 }))
 , _optional_property_change_connection(_properties->on_optional_property_changed([&](auto value) {
    _optional_property_changed_value = value;
    _optional_property_callback_counter++;
 }))
 {}

ReadwritePropertyData HostPropertyHelperImpl::readwrite_property_data() noexcept {
    return ReadwritePropertyData(
        _readwrite_property_callback_counter,
        _readwrite_property_changed_value,
        _properties->get_readwrite_property()
    );
}

void HostPropertyHelperImpl::modify_host_readwrite_property() noexcept {
    _properties->set_readwrite_property(2L);
}

ReadonlyPropertyData HostPropertyHelperImpl::readonly_property_data() noexcept {
    return ReadonlyPropertyData(
        _readonly_property_callback_counter,
        _readonly_property_changed_value,
        _properties->get_readonly_property()
    );
}

OptionalPropertyData HostPropertyHelperImpl::optional_property_data() noexcept {
    return OptionalPropertyData(
        _optional_property_callback_counter,
        _optional_property_changed_value,
        _properties->get_optional_property()
    );
}

} // namespace test::properties
