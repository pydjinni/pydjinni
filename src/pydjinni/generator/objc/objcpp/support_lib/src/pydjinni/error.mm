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
// clang-format off
#include <Foundation/Foundation.h>
#include "pydjinni/objc/error.h"
#include <exception>
// clang-format on
static_assert(__has_feature(objc_arc), "Djinni requires ARC to be enabled for this file");

namespace pydjinni {

[[noreturn]] __attribute__((weak)) void throwUnimplemented(const char * /*ctx*/, NSString * message) {
    [NSException raise:NSInternalInconsistencyException format:@"Unimplemented: %@", message];
    __builtin_unreachable();
}

const char *objc_exception::what() const noexcept {
    return [error.localizedDescription UTF8String];
}

auto objc_exception::fromCpp(const objc_exception& e) -> NSError * {
    return e.error;
}

auto objc_exception::fromCpp(const std::exception &e) -> NSError * {
    NSString *desc = NSLocalizedString([NSString stringWithUTF8String:e.what()], @"");
    NSDictionary *userInfo = @{ NSLocalizedDescriptionKey : desc};
    return [NSError errorWithDomain:@"PyDjinniDefaultErrorDomain"
                               code:0
                           userInfo:userInfo];
}

auto objc_exception::toCpp(NSError *error) -> objc_exception {
    return objc_exception{error};
}

} // namespace pydjinni
