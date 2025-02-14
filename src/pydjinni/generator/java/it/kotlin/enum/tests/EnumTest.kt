import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import test.enum_test.Helper
import test.enum_test.ExampleEnum

class TestEnum {
    @Test
    fun testEnum() {
        val exampleEnum = Helper.getEnum(ExampleEnum.A)
        assertEquals(ExampleEnum.A, exampleEnum)
    }
}
