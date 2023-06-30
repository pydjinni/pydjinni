import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.*;
import test.record.*;
import java.util.*;

class TestCollectionTypes {

    CollectionTypes record;

    @BeforeEach
    void setup() {
        record = new CollectionTypes(
            new ArrayList<>(List.of(0, 1)), new ArrayList<>(List.of("foo", "bar")),
            new HashSet<>(Set.of(0, 1)), new HashSet<>(Set.of("foo", "bar"))
        );
    }

    @Test
    void testCollectionTypes() {
        var returned_record = Helper.getCollectionTypes(record);

        assertEquals(2, returned_record.getIntList().size());
        assertEquals(0, returned_record.getIntList().get(0));
        assertEquals(1, returned_record.getIntList().get(1));
        assertEquals(2, returned_record.getStringList().size());
        assertEquals("foo", returned_record.getStringList().get(0));
        assertEquals("bar", returned_record.getStringList().get(1));
        assertEquals(2, returned_record.getIntSet().size());
        assertTrue(returned_record.getIntSet().contains(0));
        assertTrue(returned_record.getIntSet().contains(1));
        assertEquals(2, returned_record.getStringSet().size());
        assertTrue(returned_record.getStringSet().contains("foo"));
        assertTrue(returned_record.getStringSet().contains("bar"));
    }

    @Test
    void testToString() {
        assertEquals("test.record.CollectionTypes{intList=[0, 1],stringList=[foo, bar],intSet=[0, 1],stringSet=[bar, foo]}", record.toString());
    }

}
