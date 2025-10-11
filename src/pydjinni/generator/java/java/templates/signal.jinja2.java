/*#
Copyright 2025 jothepro

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
#*/
package {{ package }};

import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.ConcurrentHashMap;

public class Signal<T> {
    private ConcurrentHashMap<Long, OnPropertyChangedCallback<T>> slots = new ConcurrentHashMap<>();
    private AtomicLong slotCounter = new AtomicLong(0);

    public Connection connect(OnPropertyChangedCallback<T> callback) {
        long currentSlotIndex = slotCounter.incrementAndGet();
        slots.put(currentSlotIndex, callback);
        return new Connection.Host(() -> {
            slots.remove(currentSlotIndex);
        });
    }

    public void notify(T newValue) {
        slots.forEachValue(1L, callback -> {
            callback.callback(newValue);
        });
    }
}

