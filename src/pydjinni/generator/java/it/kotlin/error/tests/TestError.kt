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
import kotlinx.coroutines.future.await
import kotlinx.coroutines.test.runTest
import java.util.concurrent.ExecutionException
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionException
import test.error.Helper
import test.error.FooError
import test.error.ThrowingCallback
import test.error.AsyncThrowingCallback

class TestError {

    @Test
    fun testThrowingError() {
        val exception = assertThrows(FooError.SomethingWrong::class.java) {
            Helper.throwingError()
        }
        assertEquals("some error", exception.message)
    }

    @Test
    fun testThrowingErrorWithParameter() {
        val exception = assertThrows(FooError.SomethingWithParameters::class.java) {
            Helper.throwingWithParameters()
        }
        assertEquals("some error message", exception.message)
        assertEquals(42, exception.parameter)
    }

    @Test
    fun testThrowingErrorAsync() = runTest {
        val result = runCatching {
            Helper.throwingAsync().await()
        }.onFailure {
            assertInstanceOf(FooError.SomethingWrong::class.java, it)
            assertEquals("something wrong in coroutine", it.message)
        }
        assertTrue(result.isFailure)
    }

    @Test
    fun testThrowingCallback() {
        val exception = assertThrows(FooError.SomethingWrong::class.java) {
            Helper.throwingCallbackError(object : ThrowingCallback() {
                override fun throwingError() {
                    throw FooError.SomethingWrong("some callback error")
                }
            })
        }
        assertEquals("some callback error", exception.message)
    }

    @Test
    fun testThrowingCallbackErrorAsync() = runTest {
        val result = runCatching {
            Helper.throwingAsyncCallbackError(object : AsyncThrowingCallback() {
                override fun throwingError(): CompletableFuture<Void> {
                    return CompletableFuture.runAsync {
                        throw CompletionException(FooError.SomethingWrong("some async callback error"))
                    }
                }
            }).await()
        }.onFailure {
            assertInstanceOf(FooError.SomethingWrong::class.java, it)
            assertEquals("some async callback error", it.message)
        }
        assertTrue(result.isFailure)
    }
}
