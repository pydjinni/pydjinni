#include "catch2/catch_test_macros.hpp"
#include <iostream>
#include "pydjinni/coroutine/task.hpp"
#include "pydjinni/coroutine/callback_awaitable.hpp"

using namespace pydjinni::coroutine;

int scheduling_counter;

namespace schedule {
    void synchronous(const ContinuationRunner& runner) {
        scheduling_counter++;
        runner();
    }
}


SCENARIO("C++ coroutine management") {
    scheduling_counter = 0;

    GIVEN("a coroutine returning a value") {
        struct CoroutineFunctions {
            static task<int> function_returning_int() {
                co_return 5;
            }
        };
        WHEN("calling the coroutine `function_returning_int()`") {
            int result = -1;
            CoroutineFunctions::function_returning_int().on_success([&result](int value) {
                result = value;
            }).run(schedule::synchronous);

            THEN("the Scheduler should have been triggered once") {
                REQUIRE(scheduling_counter == 1);
            }

            THEN("the correct result should be returned") {
                REQUIRE(result == 5);
            }
        }

    }
    GIVEN("a coroutine returning void") {

        struct CoroutineFunctions {
            static task<> function_returning_void() {
                co_return;
            }
        };

        WHEN("calling the coroutine `function_returning_void()`") {
            bool called = false;
            CoroutineFunctions::function_returning_void().on_success([&called]() {
                called = true;
            }).run(schedule::synchronous);

            THEN("the Scheduler should have been triggered once") {
                REQUIRE(scheduling_counter == 1);
            }

            THEN("the callback should have been triggered") {
                REQUIRE(called);
            }
        }
    }

    GIVEN("a coroutine calling (awaiting) other coroutines") {

        struct CoroutineFunctions {
            static task<int> function_returning_int() {
                co_return 5;
            }

            static task<> function_returning_void() {
                co_return;
            }

            static task<int> function_calling_others() {
                co_await function_returning_void();
                co_return co_await function_returning_int();
            }
        };

        WHEN("calling the coroutine `function_calling_others()`") {
            int result = -1;
            CoroutineFunctions::function_calling_others().on_success([&result](int value) {
                result = value;
            }).run(schedule::synchronous);

            THEN("the Scheduler should have been triggered thrice") {
                REQUIRE(scheduling_counter == 3);
            }

            THEN("the correct result should be returned") {
                REQUIRE(result == 5);
            }

        }
    }

    GIVEN("a coroutine that throws an exception") {

        struct CoroutineFunctions {
            static task<> function_throwing_exception() {
                throw std::runtime_error("this is an expected exception");
                co_return;
            }
        };

        WHEN("calling the coroutine `function_throwing_exception()`") {
            std::string error_message;
            CoroutineFunctions::function_throwing_exception().on_error([&error_message](const std::exception_ptr& exception){
                try {
                    std::rethrow_exception(exception);
                } catch (const std::exception& e) {
                    error_message = e.what();
                }
            }).run(schedule::synchronous);

            THEN("the Scheduler should have been triggered once") {
                REQUIRE(scheduling_counter == 1);
            }

            THEN("the exception should be forwarded correctly") {
                REQUIRE(error_message == "this is an expected exception");
            }
        }
    }

    GIVEN("a function with an async callback parameter and a coroutine function calling it") {
        struct AsyncAndCoroutineFunctions {
            static void async_call(std::function<void(int)> function) {
                function(5);
            }

            static task<int> coroutine_call() {
                co_return co_await CallbackAwaitable<int>{
                    [](CallbackHandle<int>& handle){
                        async_call([&handle](int result){
                            handle.resume(result);
                        });
                    }
                };
            }
        };

        WHEN("calling the coroutine") {
            int result = -1;
            AsyncAndCoroutineFunctions::coroutine_call().on_success([&result](int value){
                result = value;
            }).run(schedule::synchronous);

            THEN("the Scheduler should have been triggered once") {
                REQUIRE(scheduling_counter == 1);
            }

            THEN("the correct result should be returned") {
                REQUIRE(result == 5);
            }
        }

    }
}
