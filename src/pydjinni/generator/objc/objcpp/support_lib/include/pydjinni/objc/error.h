//
// Copyright 2014 Dropbox, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

#pragma once
#include <exception>
#include <string>

namespace pydjinni {

// Throws an exception for an unimplemented method call.
[[noreturn]] void throwUnimplemented(const char * ctx, NSString * msg);

struct objc_exception : std::exception {
    NSError* error;
    explicit objc_exception(NSError* error) : error(error) {}
public:
    [[nodiscard]] const char* what() const noexcept override;
    static auto fromCpp(const objc_exception& e) -> ::NSError*;
    static auto fromCpp(const std::exception& e) -> ::NSError*;
    static auto toCpp(NSError* error) -> objc_exception;
};

} // namespace pydjinni

#define DJINNI_UNIMPLEMENTED(msg) \
    ::pydjinni::throwUnimplemented(__PRETTY_FUNCTION__, msg);
