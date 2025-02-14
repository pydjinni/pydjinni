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
