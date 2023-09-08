package pydjinni;

public class Property<T> extends ReadOnlyProperty<T> {
    public Property(T value) {
        super(value);
    }

    public void set(T value) {
        if(!value.equals(_value)) {
            _value = value;
            _callbacks.forEach(tCallback -> tCallback.change(_value));
        }
    }
}
