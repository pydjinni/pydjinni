//
// Copyright 2015 Dropbox, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

#pragma once

#include "proxy_cache_interface.hpp"
#include <functional>
#include <unordered_map>

#ifdef __cplusplus_cli
#include <Windows.h>

class Mutex {
    CRITICAL_SECTION _lock;
public:
    Mutex(const Mutex&) = delete;
    Mutex(Mutex&&) = delete;
    Mutex& operator=(const Mutex&) = delete;
    Mutex& operator=(Mutex&&) = delete;

    Mutex() throw() {
        InitializeCriticalSection(&_lock);
    }
    ~Mutex() throw() {
        DeleteCriticalSection(&_lock);
    }
    void lock() throw() {
        EnterCriticalSection(&_lock);
    }
    void unlock() throw() {
        LeaveCriticalSection(&_lock);
    }
};

template<class T>
class UniqueLock {
public:
    UniqueLock(T& mutex) throw() : _mutex(&mutex) {
        _mutex->lock();
    }
    ~UniqueLock() throw() {
        _mutex->unlock();
    }
private:
    T* _mutex;
};
#else // __cplusplus_cli
#include <mutex>
using Mutex = std::mutex;
template<class T> using UniqueLock = std::unique_lock<T>;
#endif // __cplusplus_cli

// """
//    This place is not a place of honor.
//    No highly esteemed deed is commemorated here.
//    Nothing valued is here.
//    This place is a message and part of a system of messages.
//    Pay attention to it!
//    Sending this message was important to us.
//    We considered ourselves to be a powerful culture.
// """
//
// From "Expert Judgment on Markers to Deter Inadvertent Human Intrusion into the Waste
// Isolation Pilot Plant", Sandia National Laboratories report SAND92-1382 / UC-721, p. F-49

namespace pydjinni {

// See comment on `get_unowning()` in proxy_cache_interface.hpp.
template <typename T> static inline auto upgrade_weak(const T & ptr) -> decltype(ptr.lock()) {
    return ptr.lock();
}
template <typename T> static inline T * upgrade_weak(T* ptr) { return ptr; }
template <typename T> static inline bool is_expired(const T & ptr) { return ptr.expired(); }
template <typename T> static inline bool is_expired(T* ptr) { return !ptr; }

/*
 * Generic proxy cache.
 *
 * This provides a general-purpose mechanism for proxies to be re-used. When we pass an object
 * across the language boundary from A to B, we must create a proxy object within language B
 * that passes calls back to language A. For example, if have a C++ object that is passed into
 * Java, we would create a Java object that owns a `shared_ptr` and has a set of native methods
 * that call in to C++.
 *
 * When we create such an object, we also want to cache a weak reference to it, so that if we
 * later pass the *same* object across the boundary, the same proxy will be returned. This is
 * necessary for correctness in some situations: for example, in the case of an `add_listener`
 * and `remove_listener` pattern.
 *
 * To reduce code size, only one GenericProxyCache need be instantiated for each language
 * boundary direction. The pointer types passed to this function can be generic, e.g. `id`,
 * `shared_ptr<void>`, `jobject`, etc.
 *
 * In the types below, "Impl" refers to some interface that is being wrapped, and Proxy refers
 * to the generated other-language object that wraps it.
 */
template <typename Traits>
class ProxyCache<Traits>::Pimpl {
    using Key = std::pair<std::type_index, UnowningImplPointer>;

public:
    /*
     * Look up an object in the proxy cache, and create a new one if not found.
     *
     * This takes a function pointer, not an arbitrary functor, because we want to minimize
     * code size: this function should only be instantiated *once* per langauge direction.
     */
    OwningProxyPointer get(const std::type_index & tag,
                           const OwningImplPointer & impl,
                           AllocatorFunction * alloc) {
        UniqueLock<Mutex> lock(m_mutex);
        UnowningImplPointer ptr = get_unowning(impl);
        auto existing_proxy_iter = m_mapping.find({tag, ptr});
        if (existing_proxy_iter != m_mapping.end()) {
            OwningProxyPointer existing_proxy = upgrade_weak(existing_proxy_iter->second);
            if (existing_proxy) {
                return existing_proxy;
            } else {
                // The weak reference is expired, so prune it from the map eagerly.
                m_mapping.erase(existing_proxy_iter);
            }
        }

        auto alloc_result = alloc(impl);
        m_mapping.emplace(Key{tag, alloc_result.second}, alloc_result.first);
        return alloc_result.first;
    }

    /*
     * Erase an object from the proxy cache.
     */
    void remove(const std::type_index & tag, const UnowningImplPointer & impl_unowning) {
        UniqueLock<Mutex> lock(m_mutex);
        auto it = m_mapping.find({tag, impl_unowning});
        if (it != m_mapping.end()) {
            // The entry in the map should already be expired: this is called from Handle's
            // destructor, so the proxy must already be gone. However, remove() does not
            // happen atomically with the proxy object becoming weakly reachable. It's
            // possible that during the window between when the weak-ref holding this proxy
            // expires and when we enter remove() and take m_mutex, another thread could have
            // created a new proxy for the same original object and added it to the map. In
            // that case, `it->second` will contain a live pointer to a different proxy object,
            // not an expired weak pointer to the Handle currently being destructed. We only
            // remove the map entry if its pointer is already expired.
            if (is_expired(it->second)) {
                m_mapping.erase(it);
            }
        }
    }

    Pimpl() = default;
private:
    struct KeyHash {
        std::size_t operator()(const Key & k) const {
            return k.first.hash_code() ^ UnowningImplPointerHash{}(k.second);
        }
    };

    struct KeyEqual {
        bool operator()(const Key & lhs, const Key & rhs) const {
            return lhs.first == rhs.first
                && UnowningImplPointerEqual{}(lhs.second, rhs.second);
        }
    };

    std::unordered_map<Key, WeakProxyPointer, KeyHash, KeyEqual> m_mapping;
    Mutex m_mutex;
};

template <typename Traits>
void ProxyCache<Traits>::cleanup(const std::shared_ptr<Pimpl> & base,
                                 const std::type_index & tag,
                                 UnowningImplPointer ptr) {
    base->remove(tag, ptr);
}

#ifdef __cplusplus_cli
/*
 * In C++/CLI (Windows), native static variables can only be initialized in the default
 * AppDomain. As that would be a huge limiting factor for the users of this library, we
 * work around it by holding the Pimpl instance in a managed class. Also, since managed
 * classes  can't hold native types by value, we keep the instance as a pointer to
 * shared_ptr, instantiate it in the static constructor, and schedule it's deletion to take
 * place when the current AppDomain gets unloaded.
 */
template <typename Traits>
private ref class SingletonHolder {
private:
    using Pimpl = typename ProxyCache<Traits>::Pimpl;
    using PimplPtr = std::shared_ptr<Pimpl>;
    static PimplPtr* _instance;
    static SingletonHolder() {
        _instance = new PimplPtr(new Pimpl);
        System::AppDomain::CurrentDomain->DomainUnload += gcnew System::EventHandler(&OnDomainUnload);
    }
    static void OnDomainUnload(System::Object^, System::EventArgs^) {
        System::AppDomain::CurrentDomain->DomainUnload -= gcnew System::EventHandler(&OnDomainUnload);
        delete _instance;
    }
public:
    static property PimplPtr* Instance {
        PimplPtr* get() {
            return _instance;
        }
    }
};
#endif // __cplusplus_cli

/*
 * Magic-static singleton.
 *
 * It's possible for someone to hold Djinni-static objects in a global (like a shared_ptr
 * at namespace scope), which can cause problems at static destruction time: if the proxy
 * cache itself is destroyed before the other global, use-of-destroyed-object will result.
 * To fix this, we make it possible to take a shared_ptr to the GenericProxyCache instance,
 * so it will only be destroyed once all references are gone.
 */
template <typename Traits>
auto ProxyCache<Traits>::get_base() -> const std::shared_ptr<Pimpl> & {
#ifndef __cplusplus_cli
    static const std::shared_ptr<Pimpl> instance(new Pimpl);
    // Return by const-ref. This is safe to call any time except during static destruction.
    // Returning by reference lets us avoid touching the refcount unless needed.
    return instance;
#else // __cplusplus_cli
    return *SingletonHolder<Traits>::Instance;
#endif // __cplusplus_cli
}

template <typename Traits>
auto ProxyCache<Traits>::get(const std::type_index & tag,
                             const OwningImplPointer & impl,
                             AllocatorFunction * alloc)
        -> OwningProxyPointer {
    return get_base()->get(tag, impl, alloc);
}

} // namespace pydjinni
