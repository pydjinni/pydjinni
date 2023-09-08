#pragma once
#include <unordered_map>
#include <functional>
#include <memory>
#include "handle.hpp"

namespace pydjinni {

template<class T>
class ReadOnlyProperty {
public:
    explicit ReadOnlyProperty(T value = {}) : _value(value) {}

    T get() {
        return _value;
    }

    T operator*() {
        return get();
    }

    std::unique_ptr<Handle> on_will_change(const std::function<void()>& callback) {
        const auto key = ++_counter;
        _will_change_callbacks.insert(std::pair{key, callback});
        return std::make_unique<Handle>([&](){
            _will_change_callbacks.erase(key);
        });
    }
    std::unique_ptr<Handle> on_did_change(const std::function<void(T)>& callback) {
        const auto key = ++_counter;
        _did_change_callbacks.insert(std::pair{key, callback});
        return std::make_unique<Handle>([&](){
            _did_change_callbacks.erase(key);
        });
    }

protected:
    T _value;
    int _counter = 0;
    std::unordered_map<int, std::function<void(T)>> _did_change_callbacks = {};
    std::unordered_map<int, std::function<void()>> _will_change_callbacks = {};
};

}
