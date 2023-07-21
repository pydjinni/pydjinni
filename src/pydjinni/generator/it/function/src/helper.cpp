#include "helper.hpp"
#include <cassert>

using namespace test::function;

void Helper::named_function(const std::function<bool(int32_t)>& callback) {
    assert(callback(42));
}

void Helper::anonymous_function(const std::function<bool(int32_t)>& callback) {
    assert(callback(42));
}

std::function<bool(int32_t)> Helper::cpp_named_function() {
    return [](int32_t input){
        return input == 42;
    };
}

std::function<bool(int32_t)> Helper::cpp_anonymous_function() {
    return [](int32_t input){
        return input == 42;
    };
}

std::function<void()> Helper::cpp_function_throwing_exception() {
    return [](){
        throw std::runtime_error("shit hit the fan");
    };
}
