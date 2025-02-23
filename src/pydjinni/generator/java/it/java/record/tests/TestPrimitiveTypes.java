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
import java.time.*;

class TestPrimitiveTypes {

    PrimitiveTypes record;

    @BeforeEach
    void setup() {
        record = new PrimitiveTypes(true, (byte) 8, (short) 16, 32, 64, 32.32f, 64.64, "test string", Instant.ofEpochSecond(1688213309L));
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
        assertTrue(Instant.ofEpochSecond(1688213309L).equals(returned_record.getDateT()));
    }

    @Test
    void testPrimitiveTypesEqual() {
        var returned_record = Helper.getPrimitiveTypes(record);
        assertEquals(record, returned_record);
    }

    @Test
    void testToString() {
        assertEquals("test.record.PrimitiveTypes{booleanT=true,byteT=8,shortT=16,intT=32,longT=64,floatT=32.32,doubleT=64.64,stringT=test string,dateT=2023-07-01T12:08:29Z}", record.toString());
    }

}
