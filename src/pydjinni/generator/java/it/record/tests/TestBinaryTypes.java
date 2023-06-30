import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.*;
import test.record.*;
import java.util.*;

class TestBinaryTypes {

    BinaryTypes record;
    byte[] binaryData = {(byte)0x8F};

    @BeforeEach
    void setup() {
        record = new BinaryTypes(binaryData, binaryData);
    }

    @Test
    void testBinaryTypes() {
        var returned_record = Helper.getBinaryTypes(record);

        assertTrue(Arrays.equals(returned_record.getBinaryT(), binaryData));
        assertTrue(Arrays.equals(returned_record.getBinaryOptional(), binaryData));
    }

}
