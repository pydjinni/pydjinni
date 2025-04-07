import kotlinx.coroutines.future.await
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.future.future
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import test.async_test.Asynchronous
import test.async_test.MultiplyCallback
import test.async_test.NoParametersNoReturnCallback
import test.async_test.ThrowingCallback
import java.util.concurrent.CompletableFuture
import java.util.concurrent.ExecutionException

class TestAsync {
    private lateinit var instance: Asynchronous

    @BeforeEach
    fun setup() = runTest {
        instance = Asynchronous.getInstance().await()
    }

    @Test
    fun testAsyncAdd() = runTest {
        val result = instance.add(40, 2).await()
        assertEquals(42, result)
    }

    @Test
    fun testNoParametersNoReturn() = runTest {
        instance.noParametersNoReturn().await()
    }

    @Test
    fun testAsyncCallback() = runTest {
        val result = instance.multiplyCallback(object : MultiplyCallback() {
            override fun invoke(a: Int, b: Int): CompletableFuture<Int> {
                return future { a * b }
            }
        }).await()
        assertEquals(42, result)
    }

    @Test
    fun testAsyncNoParametersNoReturnCallback() = runTest {
        val callback = object : NoParametersNoReturnCallback() {
            var callbackInvoked = false

            override fun invoke(): CompletableFuture<Void> {
                return CompletableFuture.runAsync {
                    callbackInvoked = true
                }
            }
        }
        instance.noParametersNoReturnCallback(callback).await()
        assertTrue(callback.callbackInvoked)
    }

    @Test
    fun testAsyncThrowingException() = runTest {
        val result = runCatching {
            instance.throwingException().await()
        }.onFailure {
            assertInstanceOf(RuntimeException::class.java, it)
            assertEquals(it.message, "asynchronous runtime error")
        }
        assertTrue(result.isFailure)
    }

    @Test
    fun testAsyncThrowingExceptionCallback() = runTest {
        val callback = object : ThrowingCallback() {
            override fun invoke(): CompletableFuture<Void> {
                return CompletableFuture.runAsync {
                    throw RuntimeException("asynchronous callback runtime error")
                }
            }
        }
        val result = runCatching {
            instance.throwingCallback(callback).await()
        }.onFailure {
            assertTrue(it is RuntimeException)
            assertEquals(it.message, "asynchronous callback runtime error")
        }
        assertTrue(result.isFailure)
    }

    @Test
    fun testAsyncReturningOptional() = runTest {
        val result = instance.returningOptional().await()
        assertNull(result)
    }
}
