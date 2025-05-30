#pragma once

#include "pydjinni/coroutine/continuation_runner.hpp"
#include "pydjinni/coroutine/task.hpp"


#define ASYNC []() -> ::pydjinni::coroutine::task<>
#define RUN_SYNCHRONOUS ().run([](const pydjinni::coroutine::ContinuationRunner runner){ runner();});
