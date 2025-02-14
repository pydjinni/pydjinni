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
import test.interface_test.Calculator;
import test.interface_test.PlatformInterface;
import test.interface_test.NoParametersNoReturnCallback;

class TestInterface {
    Calculator calculator;

    @BeforeEach
    void setup() {
        calculator = Calculator.getInstance();
    }

    @Test
    void testCalculator() {
        var result = calculator.add((byte)40, (byte)2);
        assertEquals(42, result);
    }

    @Test
    void testPlatformImplementation() {
        var result = calculator.getPlatformValue(new PlatformInterface() {
            public byte getValue() {
                return 5;
            }
        });
        assertEquals(5, result);
    }

    @Test
    void testMethodNoParametersNoReturn() {
        calculator.noParametersNoReturn();
    }

    @Test
    void testMethodThrowingException() {
        Exception exception = assertThrows(RuntimeException.class, () -> calculator.throwingException());
        assertEquals("shit hit the fan", exception.getMessage());
    }

    @Test
    void testMethodNoParametersNoReturnCallback() {
        var callback = new NoParametersNoReturnCallback() {
            boolean callbackInvoked = false;
            public void invoke() {
                callbackInvoked = true;
            }
        };
        calculator.noParametersNoReturnCallback(callback);
        assertTrue(callback.callbackInvoked);
    }

}
