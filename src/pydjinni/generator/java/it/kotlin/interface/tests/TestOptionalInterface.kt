import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import test.interface_test.OptionalInterface

class TestOptionalInterface {
    private var instance: OptionalInterface? = OptionalInterface.getInstance()

    @Test
    fun testNullInterface() {
        val nullInstance: OptionalInterface? = OptionalInterface.getNullInstance()
        assertNull(nullInstance)
    }

    @Test
    fun testOptionalParameter() {
        val result: String? = instance?.optionalParameter("some optional string")
        assertNotNull(result)
        assertEquals("some optional string", result)
    }

    @Test
    fun testOptionalNullParameter() {
        val result: String? = instance?.optionalNullParameter(null)
        assertNull(result)
    }
}
