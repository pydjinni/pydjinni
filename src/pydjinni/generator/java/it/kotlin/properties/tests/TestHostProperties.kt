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

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import test.properties_test.HostProperties
import test.properties_test.HostPropertyHelper

class TestHostProperties {

    class HostPropertiesImpl : HostProperties() {
        override fun changeReadonlyProperty() {
            readonlyProperty = "changed"
        }
    }

    private lateinit var hostProperties: HostProperties
    private lateinit var helper: HostPropertyHelper

    @BeforeEach
    fun setup() {
        hostProperties = HostPropertiesImpl()
        helper = HostPropertyHelper.setup(hostProperties)
    }

    @Test
    fun testChangingReadwriteHostProperty() {
        hostProperties.readwriteProperty = 42L
        val result = helper.readwritePropertyData()
        assertEquals(1, result.changeCounter)
        assertEquals(42L, result.callbackValue)
        assertEquals(42L, result.readValue)
    }

    @Test
    fun testChangingReadonlyHostProperty() {
        hostProperties.changeReadonlyProperty()
        val result = helper.readonlyPropertyData()
        assertEquals(1, result.changeCounter)
        assertEquals("changed", result.callbackValue)
        assertEquals("changed", result.readValue)
    }

    @Test
    fun testChangingHostPropertyFromHelper() {
        var callbackResult: Long = 0L
        val connection = hostProperties.onReadwritePropertyChanged({ newValue -> 
            callbackResult = newValue
        })
        helper.modifyHostReadwriteProperty()
        val result = helper.readwritePropertyData()
        assertEquals(2L, hostProperties.readwriteProperty)
        assertEquals(2L, callbackResult);
        assertEquals(1, result.changeCounter)
        assertEquals(2L, result.callbackValue)
        assertEquals(2L, result.readValue)
    }

    @Test
    fun testChangingOptionalHostPropertyNonnull() {
        hostProperties.optionalProperty = 42L
        val result = helper.optionalPropertyData()
        assertEquals(1, result.changeCounter)
        assertEquals(42L, result.callbackValue)
        assertEquals(42L, result.readValue)
    }

    @Test
    fun testChangingOptionalHostPropertyNil() {
        hostProperties.optionalProperty = null
        val result = helper.optionalPropertyData()
        assertEquals(1, result.changeCounter)
        assertEquals(null, result.callbackValue)
        assertEquals(null, result.readValue)
    }
}
