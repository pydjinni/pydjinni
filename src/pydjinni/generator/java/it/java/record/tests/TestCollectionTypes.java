// Copyright 2023 jothepro
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

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
            new HashSet<>(Set.of(0, 1)), new HashSet<>(Set.of("foo", "bar")),
            new HashMap<>(Map.of(0, 1)),
            new HashMap<>(Map.of("foo", "bar"))
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

        assertEquals(1, returned_record.getIntIntMap().size());
        assertEquals(1, returned_record.getIntIntMap().get(0));

        assertEquals(1, returned_record.getStringStringMap().size());
        assertEquals("bar", returned_record.getStringStringMap().get("foo"));
    }

    @Test
    void testToString() {
        assertEquals("test.record.CollectionTypes{intList=[0, 1],stringList=[foo, bar],intSet=[0, 1],stringSet=[bar, foo],intIntMap={0=1},stringStringMap={foo=bar}}", record.toString());
    }

}
