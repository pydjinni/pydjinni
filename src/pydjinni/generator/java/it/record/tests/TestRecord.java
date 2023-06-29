import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import test.record.Foo;
import test.record.Helper;
import java.util.ArrayList;
import java.util.List;

class TestRecord {
    @Test
    void testGetRecord() {
        var foo = new Foo(true, (byte) 8, (short) 16, 32, 64, 32.32f, 64.64, "test string", new ArrayList<>(List.of(0, 1)), new ArrayList<>(List.of("foo", "bar")), 42, "optional");
        var new_foo = Helper.getFoo(foo);
        assertEquals(true, new_foo.getBooleanT());
        assertEquals((byte) 8, new_foo.getByteT());
        assertEquals((short) 16, new_foo.getShortT());
        assertEquals(32, new_foo.getIntT());
        assertEquals(64, new_foo.getLongT());
        assertTrue(new_foo.getFloatT() > 32);
        assertTrue(new_foo.getFloatT() < 33);
        assertTrue(new_foo.getDoubleT() > 64);
        assertTrue(new_foo.getDoubleT() < 65);
        assertEquals("test string", new_foo.getStringT());
        assertEquals(2, new_foo.getIntList().size());
        assertEquals(0, new_foo.getIntList().get(0));
        assertEquals(1, new_foo.getIntList().get(1));
        assertEquals(2, new_foo.getStringList().size());
        assertEquals("foo", new_foo.getStringList().get(0));
        assertEquals("bar", new_foo.getStringList().get(1));
        assertEquals(42, new_foo.getIntOptional());
        assertEquals(Integer.class, new_foo.getIntOptional().getClass());
        assertEquals("optional", new_foo.getStringOptional());
    }

    @Test
    void testConstValue() {
        assertEquals(true, Foo.BOOLEAN_C);
        assertEquals((byte) 8, Foo.BYTE_C);
        assertEquals((short) 16, Foo.SHORT_C);
        assertEquals(32, Foo.INT_C);
        assertEquals(64, Foo.LONG_C);
        assertTrue(Foo.FLOAT_C > 32);
        assertTrue(Foo.FLOAT_C < 33);
        assertTrue(Foo.DOUBLE_C > 64);
        assertTrue(Foo.DOUBLE_C < 65);
    }

    @Test
    void testToString() {
        var foo = new Foo(true, (byte) 8, (short) 16, 32, 64, 32.32f, 64.64, "test string", new ArrayList<>(List.of(0, 1)), new ArrayList<>(List.of("foo", "bar")), 42, "optional");
        assertEquals("test.record.Foo{booleanT=true,byteT=8,shortT=16,intT=32,longT=64,floatT=32.32,doubleT=64.64,stringT=test string,intList=[0, 1],stringList=[foo, bar],intOptional=42,stringOptional=optional}", foo.toString());
    }

}
