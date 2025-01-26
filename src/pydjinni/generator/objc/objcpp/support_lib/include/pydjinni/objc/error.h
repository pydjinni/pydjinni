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

// Helper function for exception translation. Do not call directly!
[[noreturn]] void throwNSExceptionFromCurrent(const char * ctx);

struct objc_exception : std::exception {
    const std::string message;
    const std::string domain;
    const int code;

    objc_exception(const std::string_view& message, const std::string_view& domain, int code)
    : message(message), domain(domain), code(code) {}

    [[nodiscard]] const char* what() const noexcept override {
        return message.c_str();
    }

    static auto fromCpp(const objc_exception& e) -> ::NSError* {
        NSString *desc = NSLocalizedString([NSString stringWithUTF8String:e.what()], @"");
        NSDictionary *userInfo = @{ NSLocalizedDescriptionKey : desc};
        return [NSError errorWithDomain:[NSString stringWithUTF8String:e.domain.c_str()]
                                   code:e.code
                               userInfo:userInfo];
    }

    static auto fromCpp(const std::exception& e) -> ::NSError* {
        NSString *desc = NSLocalizedString([NSString stringWithUTF8String:e.what()], @"");
        NSDictionary *userInfo = @{ NSLocalizedDescriptionKey : desc};
        return [NSError errorWithDomain:@"PyDjinniDefaultErrorDomain"
                                   code:0
                               userInfo:userInfo];
    }

    static auto toCpp(const NSError* error) -> objc_exception {
        return {{[error.localizedDescription UTF8String]}, {[error.domain UTF8String]}, (int)error.code};
    }
};

} // namespace pydjinni

#define DJINNI_UNIMPLEMENTED(msg) \
    ::pydjinni::throwUnimplemented(__PRETTY_FUNCTION__, msg);

#define DJINNI_TRANSLATE_EXCEPTIONS() \
    catch (const std::exception & e) { \
        ::pydjinni::throwNSExceptionFromCurrent(__PRETTY_FUNCTION__); \
    }
