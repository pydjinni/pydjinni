import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;
import test.interface_test.Calculator;

class TestInterface {
    @Test
    void testCalculator() {
        var calculator = Calculator.getInstance();
        var result = calculator.add((byte)40, (byte)2);
        assertEquals(result, 42);
    }

}