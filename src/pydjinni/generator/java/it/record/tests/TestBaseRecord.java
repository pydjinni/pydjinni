import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.*;
import test.record.*;
import java.util.*;
import java.time.*;

class TestBaseRecord {

    @Test
    void testCppBaseRecord() {
        var record = Helper.getCppBaseRecord();
        assertEquals(42, record.getValue());
    }

    @Test
    void testJavaBaseRecord() {
        var record = new BaseRecord();
        var returned_record = Helper.getHostBaseRecord(record);
        assertEquals(42, returned_record.getValue());
    }

}
