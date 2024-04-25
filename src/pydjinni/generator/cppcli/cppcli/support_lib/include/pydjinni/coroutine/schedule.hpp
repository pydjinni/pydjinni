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

#pragma once

#include "pydjinni/coroutine/continuation_runner.hpp"
#include "pydjinni/coroutine/callback_awaitable.hpp"
#include "pydjinni/cppcli/AutoPtr.hpp"
#include "pydjinni/cppcli/Marshal.hpp"

namespace pydjinni::coroutine::schedule {

    ref class ContinuationRunnerProxy {
    private:
        AutoPtr<pydjinni::coroutine::ContinuationRunner> _continuationRunner;
    public:
        ContinuationRunnerProxy(const pydjinni::coroutine::ContinuationRunner& runner): _continuationRunner(new pydjinni::coroutine::ContinuationRunner(runner)) {}
        void Invoke() {
            _continuationRunner->run();
        }
    };

    inline void dotnet(const pydjinni::coroutine::ContinuationRunner& runner) {
        System::Threading::Tasks::Task::Run(gcnew System::Action(gcnew ContinuationRunnerProxy(runner), &ContinuationRunnerProxy::Invoke));
    }

}
