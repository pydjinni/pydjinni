// Copyright 2021 cross-language-cpp
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

#pragma once

#include <msclr\marshal_cppstd.h>

namespace pydjinni {

// Throws an exception for an unimplemented method call.
void ThrowUnimplemented(const char * ctx, const char * msg);

// Helper function for exception translation. Do not call directly!
void ThrowNativeExceptionFromCurrent(const char * ctx);

class CppCliException : public std::exception {
public:
    CppCliException(System::Exception^ exception);

    const char* what() const noexcept override;

    static System::Exception^ FromCpp(const CppCliException& e) {
        return e.exception;
    }

    static System::Exception^ FromCpp(const std::exception& e) {
        return gcnew System::Exception(msclr::interop::marshal_as<System::String^>(e.what()));
    }
private:
    gcroot<System::Exception^> exception;
    const std::string message;
};

}

#define DJINNI_UNIMPLEMENTED(msg) \
    ::pydjinni::ThrowUnimplemented(__FUNCTION__, msg); \
    return nullptr; // Silence warning C4715: not all control paths return a value

#define DJINNI_TRANSLATE_EXCEPTIONS() \
    catch (const std::exception&) { \
        ::pydjinni::ThrowNativeExceptionFromCurrent(__FUNCTION__); \
    }


