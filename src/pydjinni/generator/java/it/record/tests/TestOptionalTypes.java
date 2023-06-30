import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.*;
import test.record.*;
import java.util.*;

class TestOptionalTypes {

    OptionalTypes record;

    @BeforeEach
    void setup() {
        record = new OptionalTypes(42, "optional");
    }

    @Test
    void testOptionalTypes() {
            var returned_record = Helper.getOptionalTypes(record);

            assertEquals(42, returned_record.getIntOptional());
            assertEquals(Integer.class, returned_record.getIntOptional().getClass());
            assertEquals("optional", returned_record.getStringOptional());
    }

    @Test
    void testToString() {
        assertEquals("test.record.OptionalTypes{intOptional=42,stringOptional=optional}", record.toString());
    }

}
