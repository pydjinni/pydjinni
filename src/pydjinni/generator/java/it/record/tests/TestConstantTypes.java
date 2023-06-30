import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.*;
import test.record.*;
import java.util.*;

class TestConstantTypes {
    @Test
    void testConstantTypes() {
        assertEquals(true, ConstantTypes.BOOLEAN_C);
        assertEquals((byte) 8, ConstantTypes.BYTE_C);
        assertEquals((short) 16, ConstantTypes.SHORT_C);
        assertEquals(32, ConstantTypes.INT_C);
        assertEquals(64, ConstantTypes.LONG_C);
        assertTrue(ConstantTypes.FLOAT_C > 32);
        assertTrue(ConstantTypes.FLOAT_C < 33);
        assertTrue(ConstantTypes.DOUBLE_C > 64);
        assertTrue(ConstantTypes.DOUBLE_C < 65);
    }
}
