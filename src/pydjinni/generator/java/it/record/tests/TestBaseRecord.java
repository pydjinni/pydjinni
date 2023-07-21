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

}
