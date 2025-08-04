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
import org.junit.jupiter.api.Test
import test.properties_test.CppProperties

class TestProperties {

    private var properties: CppProperties = CppProperties.getInstance()

    @Test
    fun testPropertySetter() {
        properties.readwriteProperty = 42;
        assertEquals(42L, properties.readwriteProperty)
    }

    @Test
    fun testPropertyChangeNotification() {
        var callbackResult: Long = 0L
        val handle = properties.onReadwritePropertyChanged({ newValue -> 
            callbackResult = newValue
        })
        properties.readwriteProperty = 42;
        assertEquals(42L, callbackResult)
    }

    @Test
    fun testReadonlyPropertyChangedThroughSideEffect() {
        var callbackResult = "uncalled"
        val connection = properties.onReadonlyPropertyChanged { newValue ->
            callbackResult = newValue
        }
        properties.changeReadonlyProperty()
        assertEquals("changed", properties.readonlyProperty)
        assertEquals("changed", callbackResult)
    }

    @Test
    fun testOptionalPropertyNonnullValue() {
        var callbackResult: Long? = 0L
        val connection = properties.onOptionalPropertyChanged { newValue ->
            callbackResult = newValue
        }
        properties.optionalProperty = 42L
        assertEquals(42L, properties.optionalProperty)
        assertEquals(42L, callbackResult)
    }

    @Test
    fun testOptionalPropertyNullValue() {
        var callbackResult: Long? = 0L
        val connection = properties.onOptionalPropertyChanged { newValue ->
            callbackResult = newValue
        }
        properties.optionalProperty = null
        assertEquals(null, properties.optionalProperty)
        assertEquals(null, callbackResult)
    }
}
