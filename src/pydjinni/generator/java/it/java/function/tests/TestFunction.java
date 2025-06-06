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
import test.function_test.*;
import java.util.*;
import java.time.*;

class TestFunction {

    @Test
    void testNamedFunction() {
        Helper.namedFunction(input -> {
            return input.equals("foo");
        });
    }

    @Test
    void testAnonymousFunction() {
        Helper.anonymousFunction(input -> {
            return input.equals("foo");
        });
    }

    @Test
    void testCppNamedFunction() {
        var function = Helper.cppNamedFunction();
        var result = function.invoke("foo");
        assertTrue(result);
    }

    @Test
    void testCppAnonymousFunction() {
        var function = Helper.cppAnonymousFunction();
        var result = function.invoke("foo");
        assertTrue(result);
    }

    @Test
    void testCppFunctionThrowingException() {
        var function = Helper.cppFunctionThrowingException();
        Exception exception = assertThrows(RuntimeException.class, () -> function.invoke());
        assertEquals("shit hit the fan", exception.getMessage());
    }

    @Test
    void testCppFunctionThrowingBarError() {
        var function = Helper.cppFunctionThrowingBarError();
        Exception exception = assertThrows(Bar.BadStuff.class, () -> function.invoke());
        assertEquals("this lambda has thrown an exception", exception.getMessage());
    }

    @Test
    void testAnonymousFunctionPassingRecord() {
        Helper.anonymousFunctionPassingRecord(foo -> {
            return foo.getA() == 32;
        });
    }

    @Test
    void testFunctionParameterThrowing() {
        Exception exception = assertThrows(RuntimeException.class, () -> Helper.functionParameterThrowing(() -> {
            throw new RuntimeException("unexpected error from host");
        }));
        assertEquals("unexpected error from host", exception.getMessage());
    }

    @Test
    void testOptionalFunctionPassingNull() {
        var result = Helper.optionalFunctionPassingNull(null);
        assertNull(result);
    }

    @Test
    void testOptionalFunctionPassingFunction() {
        var result = Helper.optionalFunctionPassingFunction(input -> {
            return input.equals("foo");
        });
        assertNotNull(result);
        assertTrue(result.invoke("foo"));
    }
}
