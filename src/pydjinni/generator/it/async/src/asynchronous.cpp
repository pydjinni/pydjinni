// Copyright 2024 jothepro
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

#include "asynchronous.hpp"
#include "asynchronous_impl.hpp"

using namespace test::async_test;

pydjinni::coroutine::task<std::shared_ptr<::test::async_test::Asynchronous>> Asynchronous::get_instance() noexcept {
    co_return std::make_shared<AsynchronousImpl>();
}
