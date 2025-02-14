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
