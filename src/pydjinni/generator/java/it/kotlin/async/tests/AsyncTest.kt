import kotlinx.coroutines.future.await
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.future.future
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import test.async_test.kotlin.Asynchronous
import test.async_test.kotlin.MultiplyCallback
import test.async_test.kotlin.NoParametersNoReturnCallback
import test.async_test.kotlin.ThrowingCallback
import java.util.concurrent.ExecutionException

class TestAsync {
    private lateinit var instance: Asynchronous

    @BeforeEach
    fun setup() = runTest {
        instance = Asynchronous.getInstance()
    }

    @Test
    fun testAsyncAdd() = runTest {
        val result = instance.add(a=40, b=2)
        assertEquals(42, result)
    }

    @Test
    fun testNoParametersNoReturn() = runTest {
        instance.noParametersNoReturn()
    }

    @Test
    fun testAsyncCallback() = runTest {
        val result = instance.multiplyCallback(object : MultiplyCallback {
            override suspend fun invoke(a: Int, b: Int): Int {
                return a * b
            }
        })
        assertEquals(42, result)
    }

    @Test
    fun testAsyncNoParametersNoReturnCallback() = runTest {
        val callback = object : NoParametersNoReturnCallback {
            var callbackInvoked = false

            override suspend fun invoke() {
                callbackInvoked = true
            }
        }
        instance.noParametersNoReturnCallback(callback)
        assertTrue(callback.callbackInvoked)
    }

    @Test
    fun testAsyncThrowingException() = runTest {
        val result = runCatching {
            instance.throwingException()
        }.onFailure {
            assertInstanceOf(RuntimeException::class.java, it)
            assertEquals(it.message, "asynchronous runtime error")
        }
        assertTrue(result.isFailure)
    }

    @Test
    fun testAsyncThrowingExceptionCallback() = runTest {
        val callback = object : ThrowingCallback {
            override suspend fun invoke() {
                throw RuntimeException("asynchronous callback runtime error")
            }
        }
        val result = runCatching {
            instance.throwingCallback(callback)
        }.onFailure {
            assertTrue(it is RuntimeException)
            assertEquals(it.message, "asynchronous callback runtime error")
        }
        assertTrue(result.isFailure)
    }

    @Test
    fun testAsyncReturningOptional() = runTest {
        val result = instance.returningOptional()
        assertNull(result)
    }
}
