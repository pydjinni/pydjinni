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
import test.external_types.*;
import test.exported_types.*;
import java.util.*;
import java.time.*;

class TestExternalTypes {

    @Test
    void testUsingExternalTypes() {
        var result = MainInterface.useExternalTypes(
            test.exported_types.foo.EnumType.A,
            EnumSet.of(FlagsType.A),
            new RecordType(4, 2, "cool"),
            () -> { return true; }
        );
        assertTrue(result);
    }

    @Test
    void testUsingExternalInterface() {
        var result = InterfaceType.someMethod();
        assertTrue(result);
    }
}
