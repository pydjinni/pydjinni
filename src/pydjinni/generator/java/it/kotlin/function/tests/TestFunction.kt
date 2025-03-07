import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import test.function_test.*

class TestFunction {

    @Test
    fun testNamedFunction() {
        Helper.namedFunction { input -> input == "foo" }
    }

    @Test
    fun testAnonymousFunction() {
        Helper.anonymousFunction { input -> input == "foo" }
    }

    @Test
    fun testCppNamedFunction() {
        val function = Helper.cppNamedFunction()
        val result = function("foo")
        assertTrue(result)
    }

    @Test
    fun testCppAnonymousFunction() {
        val function = Helper.cppAnonymousFunction()
        val result = function("foo")
        assertTrue(result)
    }

    @Test
    fun testCppFunctionThrowingException() {
        val function = Helper.cppFunctionThrowingException()
        val exception = assertThrows(RuntimeException::class.java) { function() }
        assertEquals("shit hit the fan", exception.message)
    }

    @Test
    fun testCppFunctionThrowingBarError() {
        val function = Helper.cppFunctionThrowingBarError()
        val exception = assertThrows(Bar.BadStuff::class.java) { function() }
        assertEquals("this lambda has thrown an exception", exception.message)
    }

    @Test
    fun testAnonymousFunctionPassingRecord() {
        Helper.anonymousFunctionPassingRecord { foo -> foo.a == 32 }
    }

    @Test
    fun testFunctionParameterThrowing() {
        val exception = assertThrows(RuntimeException::class.java) {
            Helper.functionParameterThrowing { throw RuntimeException("unexpected error from host") }
        }
        assertEquals("unexpected error from host", exception.message)
    }

    @Test
    fun testFunctionPassingNull() {
        val result = Helper.optionalFunctionPassingNull(null)
        assertNull(result)
    }

    @Test
    fun testOptionalFunctionPassingFunction() {
        val result = Helper.optionalFunctionPassingFunction { input ->
            input == "foo"
        }
        assertNotNull(result)
        assertTrue(result!!("foo"))
    }
}
