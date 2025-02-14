import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import test.interface_test.Calculator
import test.interface_test.PlatformInterface
import test.interface_test.NoParametersNoReturnCallback

class TestInterface {
    private var calculator: Calculator = Calculator.getInstance()

    @Test
    fun testCalculator() {
        val result = calculator.add(40.toByte(), 2.toByte())
        assertEquals(42.toByte(), result)
    }

    @Test
    fun testPlatformImplementation() {
        val result = calculator.getPlatformValue(object : PlatformInterface() {
            override fun getValue(): Byte {
                return 5
            }
        })
        assertEquals(5.toByte(), result)
    }

    @Test
    fun testMethodNoParametersNoReturn() {
        calculator.noParametersNoReturn()
    }

    @Test
    fun testMethodThrowingException() {
        val exception = assertThrows(RuntimeException::class.java) {
            calculator.throwingException()
        }
        assertEquals("shit hit the fan", exception.message)
    }

    @Test
    fun testMethodNoParametersNoReturnCallback() {
        var callbackInvoked = false
        val callback = object : NoParametersNoReturnCallback() {
            override fun invoke() {
                callbackInvoked = true
            }
        }
        calculator.noParametersNoReturnCallback(callback)
        assertTrue(callbackInvoked)
    }
}
