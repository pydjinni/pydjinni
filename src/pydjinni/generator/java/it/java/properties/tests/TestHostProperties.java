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
import test.properties_test.HostProperties;
import test.properties_test.HostPropertyHelper;
import test.properties_test.ReadwritePropertyData;
import test.properties_test.ReadonlyPropertyData;
import test.properties_test.OptionalPropertyData;

class TestHostProperties {

    static class HostPropertiesImpl extends HostProperties {
        @Override
        public void changeReadonlyProperty() {
            this.setReadonlyProperty("changed");
        }
    }

    HostProperties hostProperties;
    HostPropertyHelper helper;

    @BeforeEach
    void setup() {
        hostProperties = new HostPropertiesImpl();
        helper = HostPropertyHelper.setup(hostProperties);
    }

    @Test
    void testChangingReadwriteHostProperty() {
        hostProperties.setReadwriteProperty(42L);
        ReadwritePropertyData result = helper.readwritePropertyData();
        assertEquals(1, result.getChangeCounter());
        assertEquals(42L, result.getCallbackValue());
        assertEquals(42L, result.getReadValue());
    }

    @Test
    void testChangingReadonlyHostProperty() {
        hostProperties.changeReadonlyProperty();
        ReadonlyPropertyData result = helper.readonlyPropertyData();
        assertEquals(1, result.getChangeCounter());
        assertEquals("changed", result.getCallbackValue());
        assertEquals("changed", result.getReadValue());
    }

    @Test
    void testChangingHostPropertyFromHelper() {
        AtomicLong callbackResult = new AtomicLong(0L);
        var connection = hostProperties.onReadwritePropertyChanged(callbackResult::set);
        helper.modifyHostReadwriteProperty();
        ReadwritePropertyData result = helper.readwritePropertyData();
        assertEquals(2L, hostProperties.getReadwriteProperty());
        assertEquals(2L, callbackResult.get());
        assertEquals(1, result.getChangeCounter());
        assertEquals(2L, result.getCallbackValue());
        assertEquals(2L, result.getReadValue());
    }

    @Test
    void testChangingOptionalHostPropertyNonnull() {
        hostProperties.setOptionalProperty(42L);
        OptionalPropertyData result = helper.optionalPropertyData();
        assertEquals(1, result.getChangeCounter());
        assertEquals(42L, result.getCallbackValue());
        assertEquals(42L, result.getReadValue());
    }

    @Test
    void testChangingOptionalHostPropertyNil() {
        hostProperties.setOptionalProperty(null);
        OptionalPropertyData result = helper.optionalPropertyData();
        assertEquals(1, result.getChangeCounter());
        assertEquals(null, result.getCallbackValue());
        assertEquals(null, result.getReadValue());
    }
}
