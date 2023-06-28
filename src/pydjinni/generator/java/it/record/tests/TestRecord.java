import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import test.record.Foo;
import test.record.Helper;

class TestRecord {
    @Test
    void testGetRecord() {
        var foo = new Foo(true, (byte) 8, (short) 16, 32, 64, 32.32f, 64.64, "test string");
        var new_foo = Helper.getFoo(foo);
        assertEquals(new_foo.getBooleanT(), true);
        assertEquals(new_foo.getByteT(), (byte) 8);
        assertEquals(new_foo.getShortT(), (short) 16);
        assertEquals(new_foo.getIntT(), 32);
        assertEquals(new_foo.getLongT(), 64);
        assertTrue(new_foo.getFloatT() > 32);
        assertTrue(new_foo.getFloatT() < 33);
        assertTrue(new_foo.getDoubleT() > 64);
        assertTrue(new_foo.getDoubleT() < 65);
        assertEquals(new_foo.getStringT(), "test string");
    }

    @Test
    void testConstValue() {
        assertEquals(Foo.BOOLEAN_C, true);
        assertEquals(Foo.BYTE_C, 8);
        assertEquals(Foo.SHORT_C, 16);
        assertEquals(Foo.INT_C, 32);
        assertEquals(Foo.LONG_C, 64);
        assertTrue(Foo.FLOAT_C > 32);
        assertTrue(Foo.FLOAT_C < 33);
        assertTrue(Foo.DOUBLE_C > 64);
        assertTrue(Foo.DOUBLE_C < 65);
    }

    @Test
    void testToString() {
        var foo = new Foo(true, (byte) 8, (short) 16, 32, 64, 32.32f, 64.64, "test string");
        assertEquals(foo.toString(), "test.record.Foo{booleanT=true,byteT=8,shortT=16,intT=32,longT=64,floatT=32.32,doubleT=64.64,stringT=test string}");
    }

}
