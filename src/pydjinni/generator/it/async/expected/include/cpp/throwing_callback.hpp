// AUTOGENERATED FILE - DO NOT MODIFY!
// This file was generated by PyDjinni from 'async.pydjinni'
#pragma once
#include "pydjinni/coroutine/task.hpp"
#include <memory>

namespace test::async_test {
class ThrowingCallback {
public:
    virtual ~ThrowingCallback() = default;
    virtual pydjinni::coroutine::task<void> invoke() = 0;
};
} // namespace test::async_test
