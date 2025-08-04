#pragma once
#include <functional>
#include <map>
#include <shared_mutex>
#include <ranges>
#include <memory>

namespace pydjinni::signals
{

    class connection final
    {
        std::function<void()> _disconnect;

        explicit connection(const std::function<void()>& disconnect): _disconnect(disconnect)
        {
        }

    public:
        void disconnect() const noexcept
        {
            _disconnect();
        };


        ~connection()
        {
            disconnect();
        }

        connection(connection&& obj) noexcept :_disconnect(obj._disconnect) {
            obj._disconnect = [](){};
        }

        template <typename> friend class signal;
    };

    template <typename T>
    class signal final
    {

        int _slot_counter = 0;
        const std::shared_ptr<std::shared_mutex> _mutex = std::make_shared<std::shared_mutex>();
        const std::shared_ptr<std::map<int, const std::function<void(T)>>> _slots = std::make_shared<std::map<int, const std::function<void(T)>>>();

    public:
        connection connect(const std::function<void(T)> callback) noexcept
        {
            _mutex->lock();
            _slots->insert({++_slot_counter, callback});
            _mutex->unlock();
            return connection(
                [weak_slots =std::weak_ptr(_slots), weak_mutex=std::weak_ptr(_mutex), slot = _slot_counter]() -> void
                {
                    if (const auto mutex = weak_mutex.lock())
                    {
                        mutex->lock();
                        if (const auto slots = weak_slots.lock())
                        {
                            slots->erase(slot);
                        }
                        mutex->unlock();
                    }
                });
        }

        void notify(T value) const noexcept
        {
            _mutex->lock_shared();
            for (const auto& callback : std::views::values(*_slots))
            {
                callback(value);
            }
            _mutex->unlock_shared();
        }
    };

} // namespace pydjinni::signals
