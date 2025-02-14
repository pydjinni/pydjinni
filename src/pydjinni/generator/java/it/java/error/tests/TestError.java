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
import java.util.concurrent.ExecutionException;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import test.error.Helper;
import test.error.FooError;
import test.error.ThrowingCallback;
import test.error.AsyncThrowingCallback;

class TestError {

    @Test
    void testThrowingError() {
        var exception = assertThrows(FooError.SomethingWrong.class, () -> Helper.throwingError());
        assertEquals("some error", exception.getMessage());
    }

    @Test
    void testThrowingErrorWithParameter() {
        var exception = assertThrows(FooError.SomethingWithParameters.class, () -> Helper.throwingWithParameters());
        assertEquals("some error message", exception.getMessage());
        assertEquals(42, exception.getParameter());
    }

    @Test
    void testThrowingErrorAsync() {
        Exception exception = assertThrows(ExecutionException.class, () -> Helper.throwingAsync().get());
        assertInstanceOf(FooError.SomethingWrong.class, exception.getCause());
        assertEquals("something wrong in coroutine", exception.getCause().getMessage());
    }

    @Test
    void testThrowingCallback() {
        var exception = assertThrows(FooError.SomethingWrong.class, () -> Helper.throwingCallbackError(new ThrowingCallback() {
            public void throwingError() throws FooError {
                throw new FooError.SomethingWrong("some callback error");
            }
        }));
        assertEquals("some callback error", exception.getMessage());
    }

    @Test
    void testThrowingCallbackErrorAsync() {
        Exception exception = assertThrows(ExecutionException.class, () -> Helper.throwingAsyncCallbackError(new AsyncThrowingCallback() {
            public CompletableFuture<Void> throwingError() {
                return CompletableFuture.runAsync(() -> {
                    throw new CompletionException(new FooError.SomethingWrong("some async callback error"));
                });
            }
        }).get());
        assertInstanceOf(FooError.SomethingWrong.class, exception.getCause());
        assertEquals("some async callback error", exception.getCause().getMessage());
    }

}
