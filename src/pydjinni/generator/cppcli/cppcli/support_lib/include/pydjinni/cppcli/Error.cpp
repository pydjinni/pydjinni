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

#include "Error.hpp"
#include "Marshal.hpp"

namespace pydjinni {

void ThrowUnimplemented(const char *, const char * msg) {
    throw gcnew System::NotImplementedException(msclr::interop::marshal_as<System::String^>(msg));
}

void ThrowNativeExceptionFromCurrent(const char *) {
    try {
        throw;
    } catch (const std::exception & e) {
        throw gcnew System::Exception(msclr::interop::marshal_as<System::String^>(e.what()));
    }
}

CppCliException::CppCliException(System::Exception^ exception)
        : exception(exception), message(::pydjinni::cppcli::translator::String::ToCpp(exception->Message)) {}

const char* CppCliException::what() const noexcept {
    return message.c_str();
}

}
