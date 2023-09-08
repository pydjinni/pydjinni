#pragma once
#include <functional>

namespace pydjinni {

class Handle {
public:
    Handle() = default;
    ~Handle() {
        disconnect();
    }
    void disconnect() {
        if(_active) {
            _remove();
            _active = false;
        }

    }
    explicit Handle(const std::function<void()>& remove) : _remove(remove) {};


private:
    std::function<void()> _remove;
    bool _active = true;
};

}