import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.*;
import test.record.*;
import java.util.*;

class TestPrimitiveTypes {

    PrimitiveTypes record;

    @BeforeEach
    void setup() {
        record = new PrimitiveTypes(true, (byte) 8, (short) 16, 32, 64, 32.32f, 64.64, "test string");
    }

    @Test
    void testPrimitiveTypes() {
        var returned_record = Helper.getPrimitiveTypes(record);
        assertEquals(true, returned_record.getBooleanT());
        assertEquals((byte) 8, returned_record.getByteT());
        assertEquals((short) 16, returned_record.getShortT());
        assertEquals(32, returned_record.getIntT());
        assertEquals(64, returned_record.getLongT());
        assertTrue(returned_record.getFloatT() > 32);
        assertTrue(returned_record.getFloatT() < 33);
        assertTrue(returned_record.getDoubleT() > 64);
        assertTrue(returned_record.getDoubleT() < 65);
        assertEquals("test string", returned_record.getStringT());
    }

    @Test
    void testToString() {
        assertEquals("test.record.PrimitiveTypes{booleanT=true,byteT=8,shortT=16,intT=32,longT=64,floatT=32.32,doubleT=64.64,stringT=test string}", record.toString());
    }

}
