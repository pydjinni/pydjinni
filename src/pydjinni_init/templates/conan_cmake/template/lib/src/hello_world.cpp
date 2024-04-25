#include "hello_world.hpp"

using namespace pydjinni::example;

std::string HelloWorld::say_hello() noexcept {
    return "hello from C++!";
}
