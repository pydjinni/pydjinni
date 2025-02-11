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
import test.namespace_test.GlobalInterface;
import test.namespace_test.something.namespaced.NamespacedInterface;
import test.namespace_test.GlobalRecord;
import test.namespace_test.something.namespaced.NamespacedRecord;
import test.namespace_test.something.namespaced.OtherNamespacedRecord;

class TestNamespace {

    @Test
    void testGlobalInterface() {
        var result = GlobalInterface.getNamespacedRecord();
        assertEquals(new NamespacedRecord(new GlobalRecord(new OtherNamespacedRecord(5))), result);
    }

    @Test
    void testNamespacedInterface() {
        var result = NamespacedInterface.getGlobalRecord();
        assertEquals(new GlobalRecord(new OtherNamespacedRecord(5)), result);
    }
}
