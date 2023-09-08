package pydjinni;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

public class ReadOnlyProperty<T> {

    protected T _value;
    protected List<Callback<T>> _callbacks;
    public ReadOnlyProperty(T value) {
        _value = value;
        _callbacks = Collections.synchronizedList(new ArrayList<>());
    }
    public T get() {
        return _value;
    }

    public Handle onChange(Callback<T> callback) {
        _callbacks.add(callback);
        return new Handle(() -> _callbacks.remove(callback));
    }

    @FunctionalInterface
    public interface Callback<T> {
        void change(T value);
    }

    public static class Handle {
        private final AtomicBoolean _active;
        private final HandleCallback _remove;
        private interface HandleCallback {
            void remove();
        }
        private Handle(HandleCallback remove) {
            _remove = remove;
            _active = new AtomicBoolean(true);
        }

        public void disconnect() {
            if(_active.get()) {
                _remove.remove();
                _active.set(false);
            }

        }
    }
}
