#include "helper.hpp"
#include "foo_error.hpp"
#include <cassert>

using namespace test::error;

void Helper::throwing_error() {
    throw FooError::SomethingWrong("some error");
}

void Helper::throwing_with_parameters() {
    throw FooError::SomethingWithParameters(42, "some error message");
}

::pydjinni::coroutine::task<> Helper::throwing_async() {
    throw FooError::SomethingWrong("something wrong in coroutine");
    co_return;
}

::pydjinni::coroutine::task<bool> Helper::throwing_async_with_return_value() {
    throw FooError::SomethingWrong("something wrong in coroutine with return value");
    co_return true;
}

void Helper::throwing_callback_error(const std::shared_ptr<::test::error::ThrowingCallback> &callback) {
    std::exception_ptr exceptionPtr = nullptr;
    try {
        callback->throwing_error();
    } catch (const FooError::SomethingWrong& e) {
        exceptionPtr = std::current_exception();
        assert(std::string(e.what()) == "some callback error");
    }
    assert(exceptionPtr != nullptr);
    std::rethrow_exception(exceptionPtr);
}

::pydjinni::coroutine::task<> Helper::throwing_async_callback_error(
        const std::shared_ptr<::test::error::AsyncThrowingCallback> &callback) {
    std::exception_ptr exceptionPtr = nullptr;
    try {
        co_await callback->throwing_error();
    } catch (const FooError::SomethingWrong& e) {
        exceptionPtr = std::current_exception();
        assert(std::string(e.what()) == "some async callback error");
    }
    assert(exceptionPtr != nullptr);
    std::rethrow_exception(exceptionPtr);
}

void Helper::nonstatic_throwing_error()
{
    throw FooError::SomethingWrong("some error");
}

