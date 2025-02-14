import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import test.record.*

class TestOptionalTypes {

    private val record: OptionalTypes = OptionalTypes(42, "optional")

    @Test
    fun testOptionalTypes() {
        val returnedRecord = Helper.getOptionalTypes(record)

        assertEquals(42, returnedRecord.intOptional)
        assertEquals("optional", returnedRecord.stringOptional)
        assertEquals(8, returnedRecord.stringOptional?.length)
    }

    @Test
    fun testToString() {
        assertEquals("test.record.OptionalTypes{intOptional=42,stringOptional=optional}", record.toString())
    }
}
