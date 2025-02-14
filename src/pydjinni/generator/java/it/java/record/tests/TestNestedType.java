// Copyright 2023 - 2024 jothepro
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
import java.time.*;

class TestNestedType {

    ParentType record;

    @BeforeEach
    void setup() {
        record = new ParentType(new NestedType(42, new ArrayList<>(List.of(
            new ArrayList<>(List.of(1, 2)),
            new ArrayList<>(List.of(3, 4))
        ))));
    }

    @Test
    void testNestedType() {
        var returned_record = Helper.getNestedType(record);
        assertEquals(42, returned_record.getNested().getA());
    }

    @Test
    void testToString() {
        assertEquals("test.record.ParentType{nested=test.record.NestedType{a=42,b=[[1, 2], [3, 4]]}}", record.toString());
    }

}
