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

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import test.flags_test.Helper;
import test.flags_test.ExampleFlags;
import java.util.EnumSet;

class TestFlags {
    @Test
    void testFlags() {
        var exampleFlags = Helper.getFlag(EnumSet.of(ExampleFlags.A));
        assertEquals(exampleFlags, EnumSet.of(ExampleFlags.A));
    }

    @Test
    void testAllFlags() {
        var exampleFlags = Helper.getAllFlag(EnumSet.allOf(ExampleFlags.class));
        assertEquals(exampleFlags, EnumSet.allOf(ExampleFlags.class));
    }

    @Test
    void testNoneFlags() {
        var exampleFlags = Helper.getNoneFlag(EnumSet.noneOf(ExampleFlags.class));
        assertEquals(exampleFlags, EnumSet.noneOf(ExampleFlags.class));
    }



}
