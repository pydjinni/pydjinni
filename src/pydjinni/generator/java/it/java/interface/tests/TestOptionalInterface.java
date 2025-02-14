// Copyright 2025 jothepro
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
import test.interface_test.OptionalInterface;

class TestOptionalInterface {
    OptionalInterface instance;

    @BeforeEach
    void setup() {
        instance = OptionalInterface.getInstance();
        assertNotNull(instance);
    }

    @Test
    void testNullInterface() {
        var nullInstance = OptionalInterface.getNullInstance();
        assertNull(nullInstance);
    }

    @Test
    void testOptionalParameter() {
        var result = instance.optionalParameter("some optional string");
        assertNotNull(result);
        assertEquals("some optional string", result);
    }

    @Test
    void testOptionalNullParameter() {
        var result = instance.optionalNullParameter(null);
        assertNull(result);
    }



}
