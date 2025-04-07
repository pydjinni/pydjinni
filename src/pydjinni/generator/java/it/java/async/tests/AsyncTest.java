// Copyright 2024 jothepro
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
import test.async_test.Asynchronous;
import test.async_test.MultiplyCallback;
import test.async_test.NoParametersNoReturnCallback;
import test.async_test.ThrowingCallback;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.ExecutionException;

class TestAsync {
    CompletableFuture<Asynchronous> instance;

    @BeforeEach
    void setup() throws Exception {
        instance = Asynchronous.getInstance();
    }

    @Test
    void testAsyncAdd() throws Exception {
        var result = instance.thenCompose((instance) -> instance.add(40, 2)).get();
        assertEquals(42, result);
    }

    @Test
    void testNoParametersNoReturn() throws Exception {
        instance.thenCompose((instance) -> instance.noParametersNoReturn()).get();
    }

    @Test
    void testAsyncCallback() throws Exception {
        var result = instance.thenCompose((instance) -> instance.multiplyCallback(new MultiplyCallback() {
                public CompletableFuture<Integer> invoke(int a, int b) {
                    return CompletableFuture.supplyAsync(() -> a * b);
                }
            }
        )).get();
        assertEquals(result, 42);
    }

    @Test
    void testAsyncNoParametersNoReturnCallback() throws Exception {
        var callback = new NoParametersNoReturnCallback() {
            boolean callbackInvoked = false;
            public CompletableFuture<Void> invoke() {
                return CompletableFuture.runAsync(() -> {
                    callbackInvoked = true;
                    return;
                });
            }
        };
        instance.thenCompose((instance) -> instance.noParametersNoReturnCallback(callback)).get();
        assertTrue(callback.callbackInvoked);
    }

    @Test
    void testAsyncThrowingException() throws Exception {
        Exception exception = assertThrows(ExecutionException.class, () -> {
            instance.thenCompose((instance) -> instance.throwingException()).get();
        });
        assertEquals("asynchronous runtime error", exception.getCause().getMessage());
    }

    @Test
    void testAsyncThrowingExceptionAsyncHandling() throws Exception {
        instance.thenCompose((instance) -> instance.throwingException()).handle((result, ex) -> {
            assertEquals("asynchronous runtime error", ex.getCause().getMessage());
            return 0;
        }).get();
    }

    @Test
    void testAsyncThrowingExceptionCallback() throws Exception {
        var callback = new ThrowingCallback() {
            public CompletableFuture<Void> invoke() {
                    return CompletableFuture.runAsync(() -> {
                       throw new RuntimeException("asynchronous callback runtime error");
                    });
                }
            };
        Exception exception = assertThrows(ExecutionException.class, () -> {
            instance.thenCompose((instance) -> instance.throwingCallback(callback)).get();
        });
        assertEquals("asynchronous callback runtime error", exception.getCause().getMessage());
    }

    @Test
    void testAsyncReturningOptional() throws Exception {
        var result = instance.thenCompose((instance) -> instance.returningOptional()).get();
        assertNull(result);
    }

}
