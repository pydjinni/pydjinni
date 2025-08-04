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
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.*;
import test.properties_test.CppProperties;

class TestProperties {

    CppProperties properties;

    @BeforeEach
    void setup() {
        properties = CppProperties.getInstance();
    }

    @Test
    void testPropertySetter() {
        properties.setReadwriteProperty(42L);
        assertEquals(42L, properties.getReadwriteProperty());
    }

    @Test
    void testPropertyChangeNotification() {
        AtomicLong callbackResult = new AtomicLong(0L);
        final var connection = properties.onReadwritePropertyChanged(callbackResult::set);
        properties.setReadwriteProperty(42L);
        assertEquals(42L, callbackResult.get());
    }

    @Test
    void testReadonlyProperyChangedThroughSideEffect() {
        AtomicReference<String> callbackResult = new AtomicReference<>("uncalled");
        final var connection = properties.onReadonlyPropertyChanged(callbackResult::set);
        properties.changeReadonlyProperty();
        assertEquals("changed", properties.getReadonlyProperty());
        assertEquals("changed", callbackResult.get());
    }

    @Test
    void testOptionalPropertyNonnullValue() {
        AtomicLong callbackResult = new AtomicLong(0L);
        final var connection = properties.onOptionalPropertyChanged(callbackResult::set);
        properties.setOptionalProperty(42L);
        assertEquals(42L, properties.getOptionalProperty());
        assertEquals(42L, callbackResult.get());
    }

    @Test
    void testOptionalPropertyNullValue() {
        AtomicReference<Long> callbackResult = new AtomicReference<>(0L);
        final var connection = properties.onOptionalPropertyChanged(callbackResult::set);
        properties.setOptionalProperty(null);
        assertEquals(null, properties.getOptionalProperty());
        assertEquals(null, callbackResult.get());
    }
}
