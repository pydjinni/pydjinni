import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import test.record.Foo;
import test.record.Helper;

class TestRecord {
    @Test
    void testGetRecord() {
        var foo = new Foo((byte)42);
        var new_foo = Helper.getFoo(foo);
        assertEquals(new_foo.getBar(), 42);
    }

    @Test
    void testConstValue() {
        assertEquals(Foo.BAZ, 5);
    }

    @Test
    void testToString() {
        var foo = new Foo((byte)42);
        assertEquals(foo.toString(), "test.record.Foo{bar=42}");
    }

}