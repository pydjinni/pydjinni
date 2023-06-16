import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import test.enum_test.Helper;
import test.enum_test.ExampleEnum;

class TestEnum {
    @Test
    void testEnum() {
        var exampleEnum = Helper.getEnum(ExampleEnum.A);
        assertEquals(exampleEnum, ExampleEnum.A);
    }

}