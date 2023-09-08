#pragma once
#include "read_only_property.hpp"

namespace pydjinni {

template<class T>
class Property: public ReadOnlyProperty<T> {
public:
    using ReadOnlyProperty<T>::ReadOnlyProperty;
    using ReadOnlyProperty<T>::_value;
    using ReadOnlyProperty<T>::_will_change_callbacks;
    using ReadOnlyProperty<T>::_did_change_callbacks;

    void set(const T& value) {
        if(value != _value) {
            for(const auto [key, callback]: _will_change_callbacks) {
                callback();
            }
            _value = value;
            for(const auto [key, callback]: _did_change_callbacks) {
                callback(_value);
            }
        }

    }

    Property& operator=(T value) {
        set(value);
        return *this;
    }

};

}
