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
            return input == 42;
        });
    }

    @Test
    void testAnonymousFunction() {
        Helper.anonymousFunction(input -> {
            return input == 42;
        });
    }

    @Test
    void testCppNamedFunction() {
        var function = Helper.cppNamedFunction();
        var result = function.invoke(42);
        assertTrue(result);
    }

    @Test
    void testCppAnonymousFunction() {
        var function = Helper.cppAnonymousFunction();
        var result = function.invoke(42);
        assertTrue(result);
    }

    @Test
    void testCppFunctionThrowingException() {
        var function = Helper.cppFunctionThrowingException();
        Exception exception = assertThrows(RuntimeException.class, () -> function.invoke());
        assertTrue(exception.getMessage().equals("shit hit the fan"));
    }
}
